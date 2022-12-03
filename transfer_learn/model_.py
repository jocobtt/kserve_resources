from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import load_dataset
import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import get_scheduler
from tqdm.auto import tqdm
import os
# https://neptune.ai/blog/hugging-face-pre-trained-models-find-the-best
# https://huggingface.co/docs/transformers/training

# load in our data 
dataset = load_dataset("yelp_review_full")
#dataset["train"][100] # view 100th value

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)


tokenized_datasets = dataset.map(tokenize_function, batched=True)
# if we want a smaller dataset 
small_train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(1000))
small_eval_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(1000))

# remove text column 
tokenized_datasets = tokenized_datasets.remove_columns(["text"])

# rename label column to labels
tokenized_datasets = tokenized_datasets.rename_column("label", "labels")

# set format of dataset to return pytorch tensors
tokenized_datasets.set_format("torch")

train_dataloader = DataLoader(small_train_dataset, shuffle=True, batch_size=8)
eval_dataloader = DataLoader(small_eval_dataset, batch_size=8)

model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels = 5)
# optimize model and learning rate
optimizer = AdamW(model.paramters(), lr = 5e-5)

num_epochs = 3
num_training_steps = num_epochs * len(train_dataloader)
lr_scheduler = get_scheduler(
    name="linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps
)

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model.to(device)

# training loop
progress_bar = tqdm(range(num_training_steps))
model.train()
for epoch in range(num_epochs):
    for batch in train_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        progress_bar.update(1)

PATH=os.getcwd()
torch.save(model.state_dict(), PATH)