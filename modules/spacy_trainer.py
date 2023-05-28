import json
import spacy
import random
from spacy.tokens import DocBin
from spacy.training.example import Example
from tqdm import tqdm


def load_data(file):
    with open(file, 'r') as file:
        data = json.load(file)
    return data


def save_data(file, data):
    with open(file, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def train_spacy(data, iterations):
    nlp = spacy.blank('ru')
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe('ner', last=True)

    for annotation in data['annotations']:
        for ent in annotation[1].get('entities'):
            ner.add_label(ent[2])

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        for itn in tqdm(range(iterations)):
                print("Starting iteration " + str(itn))
                random.shuffle(data.get('annotations'))
                losses = {}
                examples = []
                for text, annotations in data.get('annotations'):
                    example = Example.from_dict(nlp.make_doc(text), annotations)
                    examples.append(example)
                nlp.update(
                    examples,
                    drop=0.2,
                    sgd=optimizer,
                    losses=losses)
                print(losses)
    return (nlp)

def train():
    TRAIN_DATA = load_data('./train_data/all.json')
    nlp = train_spacy(TRAIN_DATA, 200)
    nlp.to_disk('./output/gen_all_3')


def get_train_binary():
    nlp = spacy.blank('ru')
    with open('./train_data/all.json', 'r') as file:
        data = json.load(file)['annotations']

    TRAIN_DATA = []

    for item in data:
        text = item[0]
        entities = [tuple(ent) for ent in item[1]['entities']]
        TRAIN_DATA.append((text, {'entities': entities}))

    nlp.disable_pipes(*[pipe for pipe in nlp.pipe_names if pipe != 'ner'])

    db = DocBin()

    for text, annot in tqdm(TRAIN_DATA):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annot["entities"]:
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        doc.ents = ents
        db.add(doc)

    db.to_disk("./prepared/train_all.spacy")
