# Real smartphone sensor data

`phone_acc.csv` and `phone_gyro.csv` are a real recording (236 seconds, 50 readings a second) from a smartphone worn
on the waist while a volunteer stood, sat, lay down and walked. `phone_labels.csv` says what they were doing when.
Files use the same CSV format as the free phyphox app, so your own recordings load the same way.

Source: experiment 1, user 1 of the UCI "Smartphone-Based Recognition of Human Activities and Postural Transitions"
dataset (Reyes-Ortiz, Anguita, Oneto, Parra), CC BY 4.0. https://archive.ics.uci.edu/dataset/341
Changes: trimmed to the first 11,800 samples; acceleration converted from g to m/s^2 (x 9.80665); labels added per segment.
Please cite: J.-L. Reyes-Ortiz, L. Oneto, A. Samà, X. Parra, D. Anguita. Transition-Aware Human Activity Recognition
Using Smartphones. Neurocomputing, Springer, 2015.
