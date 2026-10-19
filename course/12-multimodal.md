# 12 · Multimodal and generative modeling

Prerequisites: 03, 07–09. Outcomes: distinguish alignment from generation, calculate a contrastive example, and identify modality-specific failures. This chapter provides orientation and toy calculations, not full vision/audio training competence.

A support ticket includes a screenshot and a voice note. A useful assistant must turn pixels and sound into information without silently misreading an identifier or speaker. A modality is simply an input/output form, such as text, image or audio; start by tracking what each conversion preserves and loses.

## Representations across modalities

An encoder turns an input into a representation used by later calculations. For an image, this starts from an array of pixel intensities; audio is a sampled waveform often transformed into time-frequency features. Text is a token sequence. An image encoder may use convolutions or split an image into patches and process patch embeddings with a transformer. An audio pipeline may use frames, spectrograms or learned waveform representations. Sampling rate, resizing, cropping and normalization are part of the input contract.

Contrastive image-text learning brings matching image/caption representations together relative to nonmatching candidates. [CLIP](https://arxiv.org/abs/2103.00020) is an influential primary example. Consider two normalized image vectors (1,0) and (0,1), with matching text vectors in the same directions. Dot-product score matrix is [[1,0],[0,1]]. At temperature tau=1, each correct row probability is e/(e+1)≈.731; row negative log loss is .313. Lower tau sharpens this distribution, but shortcut cues and false negatives can still mislead training.

This objective aligns representations under training data; it does not establish complete visual understanding. Captions may omit counts, spatial relations or subtle abnormalities. Evaluate controlled counterexamples: same objects with different counts; left/right swaps; captions differing only in negation; demographic and lighting changes. A global average can hide systematic failures.

## Vision-language and speech systems

A vision-language model can project visual representations into a language model's input space or use cross-attention between modalities. It may answer questions, describe images or ground text in visual content. OCR is extraction of text from pixels; a model may confidently misread a serial number. Verify exact identifiers against dedicated checks and route low-quality scans for review.

Speech recognition maps audio to text; text-to-speech maps text to audio. Word error rate `(substitutions+deletions+insertions)/reference_words` summarizes transcription errors but not all semantic harm. One wrong medication name can matter more than several missed filler words. Diarization asks who spoke when; it is a separate task from recognition. Noise, accents, channel conditions and code-switching require explicit evaluation slices. Voice identity and private conversations introduce consent, access and retention concerns.

Worked WER: a 10-word reference has one substitution, one deletion and no insertion. WER=.2. That scalar cannot tell whether the changed word reversed a safety instruction. Add task-level semantic checks and human review where justified.

## Three generative families

This section is an optional orientation to different generation problems. An autoencoder learns to reconstruct an input through a compressed representation. A variational autoencoder introduces a latent probability distribution; training balances reconstruction likelihood with a KL regularizer toward a prior. A generative adversarial network trains a generator against a discriminator; instability and mode collapse can arise when diversity is poorly represented. Neither term is interchangeable with diffusion.

Diffusion training adds noise to data at a chosen step and learns a reverse denoising signal. Let alpha_bar_t be the fraction of signal variance retained at step t, and epsilon a standard Gaussian noise sample. A common forward form is `x_t=sqrt(alpha_bar_t)*x_0+sqrt(1-alpha_bar_t)*epsilon`, where epsilon is standard Gaussian noise and alpha_bar_t describes retained signal. With scalar x0=2, alpha_bar=.64 and epsilon=1, x_t=.8×2+.6×1=2.2. If epsilon were known exactly, reconstruction is `(2.2-.6)/.8=2`. A learned network estimates noise or related quantities imperfectly. [DDPM](https://arxiv.org/abs/2006.11239) develops a concrete probabilistic diffusion approach.

Image-generation guidance and sampling schedules trade fidelity, diversity, adherence, runtime and artifacts. A toy scalar noise calculation cannot establish that a model can synthesize realistic images. Run the numeric contrastive, denoising and WER examples in [multimodal.py](../labs/multimodal.py); no image, audio, or model download is involved.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

1. An image-text classifier scores highly on “dog” and “cat.” Does it count dogs correctly? Solution: not established; category alignment and cardinality require different evidence.
2. A scanner changes resolution. Which layer must be audited? Solution: input preprocessing, OCR/model behavior, confidence/error slices and downstream exact-field validation, not just the final prompt.
3. Why can generated images not serve as proof of a real event? Solution: realism measures perceptual plausibility, not provenance or factual occurrence. Track authentic sources and disclose synthetic content.

## Interview rehearsal and vocabulary

Interview: distinguish contrastive and generative models; compute the toy loss/noise example; design evaluation for a document assistant combining OCR, layout, retrieval and answers with modality-specific failure attribution. Vocabulary: patch, spectrogram, contrastive alignment, cross-attention, OCR, WER, diarization, latent variable, VAE, GAN, diffusion.

## What to carry forward

Cross-modal similarity, transcription and generated media answer different questions. Check the exact task and provenance rather than equating plausible output with reality. Next, [manage the histories and features behind a system](13-data-platforms.md).
