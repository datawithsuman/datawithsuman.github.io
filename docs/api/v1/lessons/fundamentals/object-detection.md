# Object Detection

> How does an object detector work, and how do you measure one?

- Track: Fundamentals › Deep Learning › Computer vision
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/object-detection/
- Before this: CNN Architectures: AlexNet to ConvNeXt (`fundamentals/cnn-architectures`), Loss Functions for Deep Learning (`fundamentals/loss-functions`)
- Quiz topic: `cnn`

## Intuition

### The situation

Your warehouse camera detector finds most boxes, but when two parcels overlap, it reports just one. Raising a setting fixes this, but now one parcel is often reported twice. A colleague shows an mAP score, and asks if it's good enough. The interviewer asks:

> How does an object detector work, and how do you measure one?

#### Why it matters

Detection appears in vision interviews and system designs: shelf checks, safety cameras, reading documents. It combines several ideas in one model, and the trade-offs between speed, accuracy and small objects are very practical. It uses a backbone and focal loss.

### The idea

Think of several people circling faces in a group photo. Many draw slightly different circles around the same face. You keep the most confident circle, and throw out those overlapping it too much. But if two faces really are close together, you might throw out a real one.

[Figure: Three families. Two-stage detectors propose and then classify. One-stage detectors predict everything in one pass. DETR predicts a set directly.]

_Boxes are compared using IoU, and judged using mAP._

### Play

**Try to break it.** Lower the NMS threshold to 0.3. Then raise it to 0.9.

#### Tune non-max suppression

Illustrative boxes and scores. Dashed: the true objects. Green: boxes kept. Faint: boxes removed. A kept box counts as correct if its IoU with an unmatched true box is at least 0.5.

Lower the threshold to **0.3**: the two overlapping objects on the left are close enough for one to delete the other. Raise it to **0.9**: duplicates survive. That's the basic weakness of NMS in crowded scenes. Now raise the minimum score, which trades recall for precision in another way.

**Now say why:** why does a low threshold lose a real object?

## Maths

### Maths

#### In one breath

A detector finds **what** is in an image and **where**, as boxes with labels and scores. Boxes are compared using **IoU**: overlap divided by combined area. Many detectors produce lots of candidates, then remove duplicates using **non-max suppression**. **Two-stage** detectors propose regions and then classify them, and **one-stage** detectors predict everything at once, which needs tricks like focal loss. **DETR** predicts a set directly. Results are measured with **mAP**.

#### The moving parts

##### IoU

IoU is the area where two boxes overlap, divided by the area they cover together. It's 0 with no overlap, and 1 for identical boxes. As an illustration, two 4×4 boxes overlapping in a 2×2 corner have IoU = 4 / 28 ≈ 0.14.

##### Anchors

An anchor is a preset box shape at each location. The network predicts whether it holds an object, and how to adjust it. Faster R-CNN uses 3 scales and 3 aspect ratios, so 9 anchors per position.

##### Non-max suppression

1. Sort the boxes by score.

2. Keep the top box.

3. Remove remaining boxes whose IoU with it exceeds a threshold.

4. Repeat with the next box still left.

##### The main designs

| Model | What it changed | A reported result |
|---|---|---|
| **R-CNN** | Runs a CNN on about 2,000 proposed regions. | 47 s per image with VGG16. |
| **Fast R-CNN** | Runs the CNN once, and pools features per region. | 0.32 s per image. 70.0 mAP on VOC 2007. |
| **Faster R-CNN** | A network proposes the regions too. | About 5 frames a second. 73.2 mAP. |
| **YOLO** | One pass, predicting boxes from a grid. | 45 frames a second. 63.4 mAP. |
| **SSD** | One pass, using feature maps at several scales. | 58 frames a second. 72.1 mAP. |
| **RetinaNet** | Focal loss for one-stage detectors. | COCO AP of 39.1, at 5 frames a second. |
| **DETR** | A Transformer predicting a set of boxes. | COCO AP of 42.0, with no anchors or NMS. |

Speeds and scores come from each paper, on different hardware, so use them to see the direction of change, not to rank models.

##### Why one-stage detectors need focal loss

They score tens of thousands of candidates per image, and nearly all are easy background. Together, those easy cases swamp the loss. Focal loss reduces their weight. It added 2.9 AP over the best balanced cross-entropy in the RetinaNet paper.

##### Set prediction in DETR

DETR predicts a fixed number of boxes, and matches them one-to-one with the true objects using the Hungarian algorithm. As each object gets just one prediction, it needs no NMS. It was weaker on small objects in the original paper.

##### What mAP means

A predicted box counts as correct if its IoU with an unmatched true box passes a threshold. Sort predictions by score, and compute the area under the precision-recall curve. That's AP for one class, and mAP averages across classes. COCO also averages across IoU thresholds from 0.50 to 0.95, which rewards tight boxes.

#### The maths

$$ \mathrm{IoU}(A,B) = \frac{|A \cap B|}{|A \cup B|}, \qquad \mathrm{FL}(p_t) = -(1-p_t)^{\gamma}\log p_t $$

IoU is the Jaccard index, as in D2L. Focal loss is from Lin et al., Equation 4.

- **IoU**: A score from 0 to 1 for how well two boxes agree.

- **the overlap**: The area shared by both boxes.

- **the combined area**: Area A plus area B, minus the overlap.

- **focal loss**: Cross-entropy, scaled down for easy examples. The RetinaNet paper’s best setting was γ = 2.

## In practice

### In practice

#### In practice

- **Small objects:** these are the usual weak spot. Use higher resolution, or feature maps at several scales.

- **Pick the metric from the use:** a safety camera needs high recall, and auto-blocking needs high precision. Check the operating point as well as mAP.

- **Crowded scenes:** NMS can remove real objects, so tune its threshold, or consider a set-based model.

- **Measure the whole pipeline:** latency includes preprocessing and NMS, not just the network.

- **Label quality matters:** loose or missing boxes limit results at high IoU thresholds. Check a sample by hand.

### The answer that sounds right

#### "High mAP means the detector is ready"

It sounds right, as mAP summarises everything. But it averages across classes, thresholds and sizes. A good score can hide poor small-object results, or a poor rare class. A deployment also runs at one threshold. Check the classes and sizes you care about, at your operating point.

## Say it

### How does an object detector work, and how do you measure one?

#### The interviewer pushes further

Follow-up 1 of 3

Walk me through non-max suppression. What's its weakness?

Sort boxes by score, keep the best, remove others overlapping it above a threshold, and repeat. Its weakness is crowded scenes: two real, overlapping objects can look like duplicates, so one gets deleted. A higher threshold keeps it, but leaves more duplicates.

Follow-up 2 of 3

What does COCO AP measure that AP at IoU 0.5 doesn't?

AP at 0.5 accepts fairly loose boxes. COCO averages across thresholds from 0.50 to 0.95, so it also rewards tight localisation. A model can score well at 0.5, yet poorly on COCO AP, if its boxes are approximately right but rarely precise.

Follow-up 3 of 3

Why is a one-stage detector harder to train than a two-stage one?

It scores every candidate location, and most are easy background, so they dominate the loss. A two-stage detector filters most of them first. Focal loss fixes this by reducing the weight of easy examples.

A detector outputs boxes, labels and scores, and IoU measures how well two boxes agree. Two-stage models like Faster R-CNN propose regions, then classify them, and tend to favour accuracy. One-stage models like YOLO and SSD predict in one pass, which favours speed. They face extreme background imbalance, so RetinaNet introduced focal loss. Most remove duplicates with non-max suppression, which can fail in crowded scenes. DETR predicts a set with one-to-one matching, so it needs no NMS. I'd measure with mAP, check small objects separately, and choose the operating point from the costs of errors.

**Key terms and sources**

IoU, anchors, non-max suppression, two-stage and one-stage detectors, focal loss, DETR's set prediction, and what mAP measures.

#### Sources

- Girshick et al., R-CNN

- Girshick, Fast R-CNN

- Ren et al., Faster R-CNN

- Redmon et al., YOLO

- Liu et al., SSD

- Lin et al., Focal Loss (RetinaNet)

- Carion et al., DETR

- D2L on anchor boxes, IoU and NMS

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
