from ultralytics import YOLO
import torch

def main():

    model = YOLO("runs\\detect\\train6\\weights\\best.pt")
    

    # Check if GPU is available and set device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"Using device: {device}")

    model.train(data="data.yaml", epochs=3000, cache=False, batch=16, workers=6, lr0=1e-1, patience=100)

if __name__ == "__main__":
    torch.multiprocessing.freeze_support()
    main()