## 개요

기존 COCO 사전학습 모델은 일반 사물 탐지를 위해 학습되어 있어,
PCB(Printed Circuit Board) 회로판 이미지를 traffic light, kite 등과 같은 비관련 객체로 잘못 인식하는 한계가 있었습니다.

이에 따라, 6개의 결함 클래스(missing_hole, mouse_bite, open_circuit, short, spur, spurious_copper)에 대한
이미지와 라벨을 제공하여 fine-tuning을 수행하였고,
이를 통해 모델이 PCB 도메인에 특화된 결함 특징을 학습하여 보다 정확하게 탐지할 수 있도록 개선했습니다.

또한, 훈련 결과 중 일부 클래스(short, spur)의 탐지 정확도가 상대적으로 낮게 나타나
이를 보완하기 위해 데이터 리샘플링(Data Resampling) 기법을 적용하여
클래스 불균형을 완화하고 탐지 성능 향상을 시도했습니다.

목적: PCB 회로판 이미지에서 다양한 결함 유형을 자동으로 탐지하고 분류하여,
시각적인 검사 과정을 자동화하고 오류 탐지의 신뢰성을 높이는 것을 목표로 합니다.

사용 클래스(6종): missing_hole, mouse_bite, open_circuit, short, spur, spurious_copper

데이터셋 출처: PCB Defect Detection Dataset by LIU XIAO LONG1

## 프로젝트 진행 흐름

    1. COCO 데이터셋으로 사전학습된 YOLOv8 모델을 사용하여 PCB 회로판 이미지에 대해 초기 예측을 수행함.
<p align="center">
      <img src="Image_results/COCO Model.jpg" width="400"><br>
      <em>Before training</em>
</p>
    
    2. PCB 오류 검출을 위한 다양한 오류가 있는 PCB 회로판 데이터셋을 사용함.
<p align="center">
  <img src="valid/images/01_PCB__8.jpg" width="200">
  <img src="valid/images/01_PCB__67.jpg" width="200">
  <img src="valid/images/01_PCB__390.jpg" width="200">
  <img src="valid/images/01_PCB__456.jpg" width="200">
</p>

<p align="center">
  <img src="valid/images/01_PCB__347.jpg" width="200">
  <img src="valid/images/01_PCB__785.jpg" width="200">
  <img src="valid/images/01_PCB__895.jpg" width="200">
  <img src="valid/images/01_PCB__966.jpg" width="200">
</p>

    3. PCB 결함 데이터셋을 기반으로 YOLOv8 모델을 Fine-tuning하여, 사전학습 모델이 PCB 도메인 특화 결함 특징을 학습하도록 함.
     
## 1차 Fine-tuning 후 모델 성능 분석

모델의 훈련 및 검증 결과를 시각화하여 탐지 성능을 분석했습니다.

<p align="center">
  <img src="runs/detect/train/results.png" width="600"><br>
  <em>모델 학습 및 손실 곡선(6·7·8번째 이미지)</em>
</p>

<p align="center">
  <img src="runs/detect/train/BoxPR_curve.png" width="600"><br>
  <em>Precision-Recall Curve</em>
</p>

<p align="center">
  <img src="runs/detect/train/confusion_matrix.png" width="600"><br>
  <em>Confusion Matrix</em>
</p>

| 항목 | 설명 |
|------|------|
| **Loss Curve** | 훈련 과정에서 손실이 안정적으로 감소하며 수렴함. |
| **Precision-Recall Curve** | mAP@0.5 = **0.989**, 클래스별 평균 0.98 이상의 높은 정밀도 |
| **Confusion Matrix** | 클래스 간 혼동이 적고, `spur` ↔ `short` 외엔 명확하게 분리됨 |
    
    4. 1차 Fine-tuning 결과, 대다수 결함 클래스에 대해 안정적인 탐지 성능을 보이지만, 'short'와 'spur' 클래스 간 혼동이 빈번하게 발생함. 이에 따라 해당 두 클래스의 학습 표본을 복사하여 데이터 리샘플링을 적용한 후 클래스 불균형 완화를 목표로 추가 Fine-tuning 실험을 진행함.

## **Data Resampling 기반 Fine-tuning 결과 비교**

<table align="center">
  <tr>
    <td align="center"><b>Baseline Fine-tuning</b></td>
    <td align="center"><b>Data Resampling<br>(Short / Spur Augmented)</b></td>
  </tr>
  <tr>
    <td align="center">
      <img src="best/val/confusion_matrix_normalized.png" width="420">
    </td>
    <td align="center">
      <img src="best/tuning val/confusion_matrix_normalized.png" width="420">
    </td>
  </tr>
</table>

| **클래스** | **Baseline** | **Data Resampling** | **해석** |
|------|------| ------| ------|
| **short** | 정확도 0.90, <br> background로 0.40 오인 | 정확도 0.89, <br> background로 0.49 오인 | **더 나빠짐**, 오히려 더 많은 short를 <br>background로 놓침(False Negative 증가) |
| **Spur** | 정확도 0.95, <br> background로 0.29 오인 | 정확도 0.94, <br> background로 0.29 오인 | 아주 조금 떨어졌으나 거의 차이 없음 |
| **mouse_bite**, <br>**open_circuit**| 정확도 0.97, <br>정확도 0.93 | 정확도 0.95, <br> 정확도 0.89 | **약간의 감소**, 미세 조정이 다른 클래스에도 영향
| **spurious_copper** | 정확도 0.97 | 정확도 0.96 | 거의 차이 없음 |
| **background** | short 0.40, <br> 나머지 | short 0.49, <br> 나머지 감소 | **배경 노이즈 영향 커짐** |

## **원인 및 해석**
1. **Data Resampling에 따른 편향 및 다양성 손실**
    - `short`, `spur`데이터만 중복·강화하면서 전체 클래스 분포가 깨졌고, <br> 그 결과 모델이 **배경과 결함 경계를 혼동**하거나 **다른 클래스의 특징을 잃는 현상(FN 증가)** 이 발생함.
    - 또한 동일 이미지의 반복 학습으로 **데이터 다양성이 감소**하여,<br> fine-tuning 과정에서 **과적합(Overfitting)** 이 유발된 것으로 추정됨.
2. **freeze 설정 영향**
    - 백본을 고정하고 헤드만 업데이트했기 때문에 <br>기존 피처맵은 그대로인데, **새로 추가된 데이터 특성을 충분히 반영하지 못했을 가능성**

## **결과 요약**
본 프로젝트에서 시행한 두 단계의 Fine-tuning 실험 결과는 다음과 같습니다:

- **Baseline**: 사전학습 모델에서 PCB 결함 특징을 탐지하도록 훈련한 모델 
- **Data Resampling**: 특정 클래스(short, spur)를 리샘플링한 모델  

| 지표 | Baseline | Data Resampling |
|------|--------|-------|
| mAP@0.5 | **0.956** | **0.933** |
| short 클래스 정확도 | 0.90 | 0.89 |
| spur 클래스 정확도 | 0.95 | 0.94 |

> **Note:** 대부분 클래스에서 성능이 오히려 하락하였음을 확인했고, 이는 **Data Resampling에 의한 편향**, **백본 Freeze 전략 미흡** 등이 주요 원인으로 분석됩니다.

## **마무리**
본 프로젝트는 **전이학습(Transfer Learning)** 이 항상 성능을 향상시키지는 않음을 보여준다.
특정 클래스 **Data Resampling**과 **freeze** 전략은 오히려 분포 편향/과적합을 유발하여 mAP50이 소폭 하락했다.
향후에는 **데이터 균형 조정**, **freeze 완화**를 통해 개선 여지를 확인했다.