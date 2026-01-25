from predict_lstm import pred

SCALE_UP_THRESHOLD = 40
SCALE_DOWN_THRESHOLD = 15

if pred > SCALE_UP_THRESHOLD:
    print("SCALE UP")
elif pred < SCALE_DOWN_THRESHOLD:
    print("SCALE DOWN")
else:
    print("KEEP CURRENT SCALE")