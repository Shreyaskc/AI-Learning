"""Learn tiny PCA/k-means representations; trace convolution and recurrence.

Standard-library arrays expose every shape. No image or external dataset.
"""
import json
import math
from foundations import dot


def center(rows):
    mean=[sum(row[j] for row in rows)/len(rows) for j in range(len(rows[0]))]
    return [[v-m for v,m in zip(row,mean)] for row in rows],mean


def principal_direction(rows,steps=60):
    centered,mean=center(rows);d=len(mean)
    covariance=[[sum(row[i]*row[j] for row in centered)/len(rows) for j in range(d)] for i in range(d)]
    vector=[1/math.sqrt(d)]*d
    for _ in range(steps):
        product=[dot(row,vector) for row in covariance];norm=math.sqrt(dot(product,product))
        if norm==0:raise ValueError('zero variance or unsuitable initial direction')
        vector=[v/norm for v in product]
    eigenvalue=dot(vector,[dot(row,vector) for row in covariance])
    return mean,vector,eigenvalue


def kmeans(rows,k=2,iterations=30):
    if not rows or k<1 or k>len(rows):raise ValueError('invalid cluster count')
    # Fixed initialization makes the demonstration reproducible, not globally optimal.
    centers=[list(rows[round(i*(len(rows)-1)/(k-1))]) for i in range(k)] if k>1 else [list(rows[0])]
    assignments=[]
    for _ in range(iterations):
        assignments=[min(range(k),key=lambda j:sum((a-b)**2 for a,b in zip(row,centers[j]))) for row in rows]
        next_centers=[]
        for j in range(k):
            group=[row for row,cluster in zip(rows,assignments) if cluster==j]
            next_centers.append([sum(row[c] for row in group)/len(group) for c in range(len(rows[0]))] if group else centers[j])
        if next_centers==centers:break
        centers=next_centers
    # Recompute to match the final returned centers even at the iteration limit.
    assignments=[min(range(k),key=lambda j:sum((a-b)**2 for a,b in zip(row,centers[j]))) for row in rows]
    inertia=sum(sum((a-b)**2 for a,b in zip(row,centers[cluster])) for row,cluster in zip(rows,assignments))
    return centers,assignments,inertia


def valid_convolution(image,kernel):
    # Correlation convention used by many deep-learning layers: kernel not flipped.
    height,width=len(image),len(image[0]);kh,kw=len(kernel),len(kernel[0])
    if kh>height or kw>width:raise ValueError('kernel larger than image')
    return [[sum(image[i+di][j+dj]*kernel[di][dj] for di in range(kh) for dj in range(kw))
             for j in range(width-kw+1)] for i in range(height-kh+1)]


def recurrent_trace(sequence):
    state=0.;trace=[]
    for value in sequence:
        state=math.tanh(value+.5*state);trace.append(state)
    return trace


def main():
    rows=[[-2.,0.],[-1.,0.],[1.,0.],[2.,0.]]
    mean,direction,eigenvalue=principal_direction(rows)
    print(json.dumps({'pca':{'mean':mean,'direction':direction,'eigenvalue':eigenvalue},
       'kmeans':kmeans(rows),'valid_convolution':valid_convolution([[1,2,3],[4,5,6],[7,8,9]],[[1,0],[0,-1]]),
       'recurrent_forward':recurrent_trace([1.,0.]),'recurrent_reversed':recurrent_trace([0.,1.]),
       'limits':'PCA power iteration can miss a leading direction with orthogonal initialization; kmeans can find local minima; convolution/RNN operations are traced, not trained'},indent=2))


if __name__=='__main__':main()
