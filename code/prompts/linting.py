from tqdm import tqdm
from openai import OpenAI
client = OpenAI(api_key="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")

nouns = ['chair']

#nouns = ['Person', 'Year', 'Way', 'Day', 'Thing', 'Man', 'World', 'Life', 'Hand', 'Part', 'Child', 'Eye', 'Woman', 'Place', 'Week', 'Case', 'Government', 'Company', 'Number', 'Group', 'Problem', 'Fact', 'Money', 'Story', 'Kid', 'Water', 'System', 'Program', 'Question', 'Work', 'Night', 'Point', 'Home', 'School', 'Book', 'Room', 'Mother', 'Area', 'History', 'Information', 'Family', 'Power', 'Hour', 'Law', 'Door', 'Health', 'City', 'Car', 'Music']

prompts = []

statementPromptsSingleNoun = [
     'Develop an ontology dedicated to {noun}.',
     'Construct an ontology focused on {noun}.',
     'Build an ontology surrounding the concept of {noun}.',
     'Formulate an ontology related to {noun}.',
     'Establish an ontology based on {noun}.',
     'Design an ontology to encompass {noun}.',
     'Generate an ontology that covers {noun}.',
     'Produce an ontology specifically for {noun}.',
     'Compose an ontology to represent {noun}.',
     'Make an ontology that pertains to {noun}.',
]

statementPromptsTheFollowingSingleNoun = [
     'Develop an ontology dedicated to the following: {noun}.',
     'Construct an ontology focused on the following: {noun}.',
     'Build an ontology surrounding the concept of the following: {noun}.',
     'Formulate an ontology related to  the following: {noun}.',
     'Establish an ontology based on the following: {noun}.',
     'Design an ontology to encompass the following: {noun}.',
     'Generate an ontology that covers the following: {noun}.',
     'Produce an ontology specifically for the following: {noun}.',
     'Compose an ontology to represent the following: {noun}.',
     'Make an ontology that pertains to the following: {noun}.'
]

questionPromptsSingleNoun = [
     "Could you develop a basic design pattern for representing {noun} in an ontology?",
     "Is it possible for you to create a straightforward pattern to depict {noun} ontologically?",
     "Can you formulate a simple ontology pattern that captures the essence of {noun}?",
     "Would you be able to generate a basic pattern for {noun}'s ontological representation?",
     "Are you able to design a simple framework within an ontology to embody {noun}?",
     "Could you craft a minimalist design pattern to illustrate {noun} within an ontology?",
     "Can you establish a basic structure for encapsulating {noun} in ontology terms?",
     "Would you create a straightforward ontology model to capture {noun}?",
     "Can you assemble a succinct pattern to convey {noun}'s concept through ontology?",
     "Could you devise a simple scheme for representing {noun} within an ontology context?"
]

questionPromptsTheFollowingSingleNoun = [
     "Could you develop a basic design pattern for representing the following in an ontology: ",
     "Is it possible for you to create a straightforward pattern to depict the following ontologically: {noun}",
     "Can you formulate a simple ontology pattern that captures the essence of the following: {noun}",
     "Would you be able to generate a basic pattern for the following's ontological representation: {noun}?",
     "Are you able to design a simple framework within an ontology to describe the following: {noun}",
     "Could you craft a minimalist design pattern to illustrate the following within an ontology: {noun}",
     "Can you establish a basic structure for encapsulating the following in ontology terms: {noun}",
     "Would you create a straightforward ontology model to capture the following: {noun}",
     "Can you assemble a succinct pattern to convey the following's concept in an ontology: {noun}",
     "Could you devise a simple scheme for representing the following within an ontology context: {noun}"
]

rdfInstructions = [
     "",
     " Provide it in valid Turtle/RDF format, excluding any extra text.",
     #" Return it in Turtle/RDF, without any additional text.",
     #" Make it in valid Turtle/RDF, without any explanatory text.",
     " Use Turtle/RDF, without any extra textual content.",
]

for i in statementPromptsSingleNoun:
          prompts.append(i)
for i in statementPromptsTheFollowingSingleNoun:
          prompts.append(i)
for i in questionPromptsSingleNoun:
     prompts.append(i)
for i in questionPromptsTheFollowingSingleNoun:
     prompts.append(i)
 
fullPrompts = []

from openai import OpenAI
client = OpenAI(api_key="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")

with open('./Results/FullPrompts.tsv', 'w') as fp:
     for noun in tqdm(nouns,desc='Nouns', position=0, leave=True):
        with open('./Results/' + noun + '.tsv', 'w') as nounFile:
            for p in tqdm(prompts, desc='Prompts', position=1, leave=False):
                for r in tqdm(rdfInstructions, desc='RDF Instructions', position=2, leave=False):
                    promptString = p.replace("{noun}", noun) + r
                    fullPrompts.append(promptString)
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": promptString,
                            }
                        ],
                        model="gpt-4",
                    )
                    response = chat_completion.choices[0].message.content
                    fp.write(noun + '\t' + p + '\t' + r + '\t' + promptString + '\t' + response.replace("\n", "") + '\n')
                    nounFile.write(p + '\t' + r + '\t' + promptString + '\t' + response.replace("\n", "") + '\n')
        nounFile.close()