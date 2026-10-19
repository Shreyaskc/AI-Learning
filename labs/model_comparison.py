"""Train/validate/test constant, logistic, CART-style tree and tanh MLP.

Synthetic IID classification only. Standard library, no network/GPU. Educational
implementations, not replacements for robust production ML libraries.
"""
import hashlib
import argparse
import json
import math
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from learning import sigmoid, logistic_loss


def make_data(count=320, seed=31):
    rng = random.Random(seed)
    rows = []
    for i in range(count):
        # Different units intentionally expose the need for train-only scaling.
        x = [rng.uniform(-1, 1), rng.uniform(-1, 1)*100]
        y = int((x[0] > 0) != (x[1] > 0))  # nonlinear XOR quadrants
        if rng.random() < .03:
            y = 1-y
        rows.append((x, y))
    return rows[:160], rows[160:240], rows[240:]


def fit_scaler(rows):
    width = len(rows[0][0])
    means = [sum(x[j] for x,y in rows)/len(rows) for j in range(width)]
    scales = [math.sqrt(sum((x[j]-means[j])**2 for x,y in rows)/len(rows)) or 1.
              for j in range(width)]
    return means, scales


def transform(rows, scaler):
    means, scales = scaler
    return [([(v-m)/s for v,m,s in zip(x,means,scales)], y) for x,y in rows]


def score(labels, probabilities):
    eps = 1e-12
    clipped = [min(1-eps,max(eps,p)) for p in probabilities]
    tp = sum(y == 1 and p >= .5 for y,p in zip(labels,probabilities))
    fp = sum(y == 0 and p >= .5 for y,p in zip(labels,probabilities))
    fn = sum(y == 1 and p < .5 for y,p in zip(labels,probabilities))
    return {'n': len(labels), 'accuracy': sum((p>=.5)==bool(y) for y,p in zip(labels,probabilities))/len(labels),
            'log_loss': -sum(y*math.log(p)+(1-y)*math.log(1-p) for y,p in zip(labels,clipped))/len(labels),
            'brier': sum((p-y)**2 for y,p in zip(labels,probabilities))/len(labels),
            'precision': tp/(tp+fp) if tp+fp else 0., 'recall': tp/(tp+fn) if tp+fn else 0.}


class Constant:
    def fit(self, rows): self.p = sum(y for x,y in rows)/len(rows); return self
    def predict(self, x): return self.p


class Logistic:
    def __init__(self, rate=.1, steps=500, l2=.001):
        self.rate, self.steps, self.l2 = rate, steps, l2
    def fit(self, rows):
        self.w = [0.]*len(rows[0][0]); self.b = 0.
        self.history = []
        for step in range(self.steps):
            gw = [self.l2*v for v in self.w]; gb = 0.
            for x,y in rows:
                error = self.predict(x)-y
                for j in range(len(self.w)): gw[j] += error*x[j]/len(rows)
                gb += error/len(rows)
            self.w = [w-self.rate*g for w,g in zip(self.w,gw)]; self.b -= self.rate*gb
            if step in (0,self.steps-1):
                self.history.append(sum(logistic_loss(sum(w*v for w,v in zip(self.w,x))+self.b,y) for x,y in rows)/len(rows))
        return self
    def predict(self, x): return sigmoid(sum(w*v for w,v in zip(self.w,x))+self.b)


@dataclass
class Node:
    probability: float
    feature: int = -1
    threshold: float = 0.
    left: object = None
    right: object = None


class Tree:
    def __init__(self, depth=4, min_leaf=8): self.depth,self.min_leaf = depth,min_leaf
    @staticmethod
    def impurity(rows):
        if not rows: return 0.
        p = sum(y for x,y in rows)/len(rows)
        return 2*p*(1-p)
    def build(self, rows, depth):
        node = Node((sum(y for x,y in rows)+1)/(len(rows)+2))
        if depth == 0 or len(rows)<2*self.min_leaf or self.impurity(rows)==0: return node
        best = None
        for j in range(len(rows[0][0])):
            values=sorted(set(x[j] for x,y in rows))
            for low,high in zip(values,values[1:]):
                threshold=(low+high)/2
                left=[row for row in rows if row[0][j]<=threshold]
                right=[row for row in rows if row[0][j]>threshold]
                if min(len(left),len(right))<self.min_leaf: continue
                cost=(len(left)*self.impurity(left)+len(right)*self.impurity(right))/len(rows)
                if best is None or cost<best[0]: best=(cost,j,threshold,left,right)
        if best is None or best[0] >= self.impurity(rows)-1e-12: return node
        _,node.feature,node.threshold,left,right=best
        node.left=self.build(left,depth-1);node.right=self.build(right,depth-1)
        return node
    def fit(self, rows): self.root=self.build(rows,self.depth);return self
    def predict(self, x):
        node=self.root
        while node.feature>=0: node=node.left if x[node.feature]<=node.threshold else node.right
        return node.probability


class MLP:
    def __init__(self, width=8, rate=.15, steps=700, seed=17, l2=.001):
        self.width,self.rate,self.steps,self.seed,self.l2=width,rate,steps,seed,l2
    def initialize(self, dimensions):
        self.dimensions=dimensions
        rng=random.Random(self.seed)
        # Flatten [input->hidden weights, hidden biases, hidden->output weights, output bias].
        self.params=([rng.uniform(-1,1)/math.sqrt(dimensions) for _ in range(self.width*dimensions)]
                     +[0.]*self.width+[rng.uniform(-1,1)/math.sqrt(self.width) for _ in range(self.width)]+[0.])
    def forward(self, x):
        h=self.width;d=self.dimensions;bstart=h*d;vstart=bstart+h
        hidden=[math.tanh(sum(self.params[j*d+k]*x[k] for k in range(d))+self.params[bstart+j]) for j in range(h)]
        logit=sum(self.params[vstart+j]*hidden[j] for j in range(h))+self.params[-1]
        return hidden,logit
    def predict(self,x): return sigmoid(self.forward(x)[1])
    def loss_gradient(self,rows):
        h=self.width;d=self.dimensions;bstart=h*d;vstart=bstart+h
        gradient=[0.]*len(self.params);loss=0.;n=len(rows)
        for x,y in rows:
            hidden,z=self.forward(x);error=sigmoid(z)-y;loss+=logistic_loss(z,y)/n
            for j in range(h):
                local=error*self.params[vstart+j]*(1-hidden[j]**2)
                for k in range(d):gradient[j*d+k]+=local*x[k]/n
                gradient[bstart+j]+=local/n;gradient[vstart+j]+=error*hidden[j]/n
            gradient[-1]+=error/n
        # Regularize weights only, not biases.
        for index in list(range(bstart))+list(range(vstart,vstart+h)):
            loss+=self.l2*self.params[index]**2/2
            gradient[index]+=self.l2*self.params[index]
        return loss,gradient
    def fit(self,rows):
        self.initialize(len(rows[0][0]));self.history=[self.loss_gradient(rows)[0]]
        for _ in range(self.steps):
            _,gradient=self.loss_gradient(rows)
            self.params=[p-self.rate*g for p,g in zip(self.params,gradient)]
        self.history.append(self.loss_gradient(rows)[0]);return self



def export_model(model, family, scaler):
    if family=='constant':state={'p':model.p}
    elif family=='logistic':state={'w':model.w,'b':model.b}
    elif family=='tree':state={'root':asdict(model.root)}
    elif family=='mlp':state={'params':model.params,'width':model.width,'dimensions':model.dimensions}
    else:raise ValueError('unknown family')
    return {'schema_version':1,'family':family,'feature_order':['x1','x2'],
            'scaler':{'means':scaler[0],'scales':scaler[1]},'state':state}


def artifact_predict(artifact, raw_features):
    if artifact['schema_version']!=1:raise ValueError('unsupported artifact version')
    if len(raw_features)!=len(artifact['feature_order']):raise ValueError('feature count mismatch')
    x=[(value-mean)/scale for value,mean,scale in zip(raw_features,artifact['scaler']['means'],artifact['scaler']['scales'])]
    family,state=artifact['family'],artifact['state']
    if family=='constant':return state['p']
    if family=='logistic':return sigmoid(sum(w*v for w,v in zip(state['w'],x))+state['b'])
    if family=='tree':
        node=state['root']
        while node['feature']>=0:node=node['left'] if x[node['feature']]<=node['threshold'] else node['right']
        return node['probability']
    if family=='mlp':
        model=MLP(width=state['width']);model.dimensions=state['dimensions'];model.params=state['params']
        return model.predict(x)
    raise ValueError('unknown artifact family')


def run():
    train,validation,test=make_data();scaler=fit_scaler(train)
    fingerprints={name:hashlib.sha256(json.dumps(rows).encode()).hexdigest() for name,rows in zip(['train','validation','test'],[train,validation,test])}
    train,validation,test=[transform(rows,scaler) for rows in (train,validation,test)]
    factories={'constant':[lambda:Constant()], 'logistic':[lambda:Logistic()],
               'tree':[lambda:Tree(depth=2),lambda:Tree(depth=4)],
               'mlp':[lambda:MLP(width=4),lambda:MLP(width=8)]}
    result={'dataset':'synthetic XOR quadrants with 3% independent label flips',
            'seed':31,'split_fingerprints':fingerprints,'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'split_counts':[len(train),len(validation),len(test)],
            'scaler_fit':'train only','threshold':.5,'selection':'lowest validation log loss within each family; test never selects',
            'limitations':'one synthetic split; unequal family tuning/compute budgets; no universal ranking or efficiency claim',
            'models':{}}
    for family,candidates in factories.items():
        fitted=[]
        for factory in candidates:
            model=factory().fit(train)
            validation_score=score([y for x,y in validation],[model.predict(x) for x,y in validation])
            fitted.append((validation_score['log_loss'],model,validation_score))
        _,model,validation_score=min(fitted,key=lambda item:item[0])
        result['models'][family]={'validation':validation_score,
                'test':score([y for x,y in test],[model.predict(x) for x,y in test]),
                'artifact':export_model(model,family,scaler),
                'training_loss_trace':getattr(model,'history',None),
                'selected_config':{k:v for k,v in vars(model).items() if k in ('width','steps','rate','depth','min_leaf','l2')}}
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
    result=run();text=json.dumps(result,indent=2,sort_keys=True)
    if args.report:args.report.write_text(text+'\n')
    print(text)


if __name__=='__main__':main()
