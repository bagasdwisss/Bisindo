import numpy as np

def process_landmarks(results):
    keypoints = np.zeros(126)
    
    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            if i >= 2: 
                break

            hand_pts = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])

            wrist = hand_pts[0]
            normalized_hand = hand_pts - wrist
            start_idx = i * 63
            end_idx = start_idx + 63
            keypoints[start_idx:end_idx] = normalized_hand.flatten()
            
    return keypoints