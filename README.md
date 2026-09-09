
This repository contains the computational workflow used in the study
# Application of the SEISBENCH framework to detect P and S waves of volcano-tectonic seismic sequences: a test using data from the Azores catalogue 

The study evaluates pretrained deep-learning seismic phase-picking models from SeisBench on local volcano-tectonic earthquake data from Santa Bárbara Volcano, Terceira Island, Azores. The repository also contains the implementation used for the STA/LTA baseline comparison, performance evaluation, and generation of the main results and figures.

## Repository purpose

The main objectives of the repository are to:

- preprocess the seismic waveform data;
- apply pretrained SeisBench phase-picking models;
- evaluate P and S-phase picking performance;
- compare the deep-learning models with an STA/LTA baseline;
- calculate precision, recall, F1-score, and ROC-based metrics;
- analyze model performance across stations and datasets;
- reproduce the main tables and figures presented in the manuscript.

The repository is intended to support the reproducibility and transparency of the computational analysis described in the paper.


## Repository structure
.  
├── README.md  
├── requirements.txt  
├── data/  
│ └── README.md  
├── source/  
│ └── ...  
├── figures/  
│ └── Supplementary_Figures.docx  
└── tables/  
  ├── Roc.ods  
  └── Supplementary_Tables.docx  
    

## Main directories
### data/ 
Contains all the metadata files  

### source/
Contains all the scripts scripts used to in this work.

### figures/
Contains figures presented in the manuscript and supplementary material.

### tables/
Contains files associated with the tables presented in the manuscript.

## Data
The seismic dataset consists of volcano-tectonic earthquakes recorded by the CIVISA seismic network around Santa Bárbara Volcano, Terceira Island, Azores.  
The dataset used in the study contains 649 events and 3463 three-component waveforms, with manually identified P and S-phase arrivals.  
The waveform data are not redistributed in this repository at this moment because of institutional restrictions.  
A description of the dataset and its characteristics is provided in the manuscript. Users with access to the corresponding seismic data can use the scripts provided here to reproduce the analysis.  
The repository may contain metadata, example files, or anonymized/processed information where permitted.

## Software requirements

The analysis was performed using Python 3.10.19.  
The main packages used include:  

ObsPy  
SeisBench  
NumPy  
Pandas  
SciPy  
Matplotlib  
h5py  
csv  
math  
os  
  
The required Python packages can be installed using:
  
    pip install -r requirements.txt

SeisBench models Th study evaluates pretrained phase-picking models available through SeisBench.  
The evaluated models include:  

| Model     | Trainig    |
| :-------- | :-------   | 
| BasicPhaseAE | ETHZ    |
| BasicPhaseAE | GEOFON    |
| BasicPhaseAE | INSTANCE  |
| BasicPhaseAE | STEAD     |
| PhaseNet   | ETHZ    |
| PhaseNet | GEOFON    |
| PhaseNet | INSTANCE  |
| PhaseNet | STEAD     |
| EQTransformer   | ETHZ    |
| EQTransformer | GEOFON    |
| EQTransformer | INSTANCE  |
| EQTransformer | STEAD     |
| GPD   | ETHZ    |
| GPD | GEOFON    |
| GPD | INSTANCE  |
| GPD | STEAD     |

The models were evaluated using their pretrained weights without local fine-tuning.

## Reference phase picks

The reference P and S-phase arrivals were manually identified using SEISAN by an experienced analyst.
A predicted phase was considered a correct pick when it occurred within ±0.5 s of the corresponding manual reference pick.
Predictions outside this tolerance window were considered false positives according to the evaluation procedure described in the manuscript.

STA/LTA baseline
The repository also contains the implementation used for the STA/LTA comparison.
The STA/LTA configuration used in the study was: STA window: 1 s LTA window: 10 s trigger threshold: detrigger threshold:, if applicable filtering: 1 - 20 Hz
sampling rate: 100 Hz

The resulting STA/LTA detections were evaluated using the same reference picks and tolerance criteria used for the deep-learning models.

## Evaluation metrics
The repository contains the scripts used to calculate:  
Precision  
Recall  
F1-score  
False-positive rate  
True-positive rate  
ROC curves

A predicted pick was matched to a manual pick when the prediction occurred within ±0.5 s of the reference arrival.

## Reproducibility
The repository provides the code used for the principal computational analyses presented in the manuscript. Because the original seismic waveform data cannot be redistributed, complete reproduction requires access to the underlying seismic recordings and associated metadata.
The repository therefore aims to provide a transparent and reusable implementation of the analysis workflow rather than a fully self-contained copy of the original dataset.

## Citation
If you use this repository or the associated workflow, please cite: (coming soon)
