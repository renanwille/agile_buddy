# Agile Buddy

Agile buddy is a command line tool (for now) that helps the user generate summaries of his work days and keep them into a folder. When he needs a summary of a couple of days before he just asks for it passing the day range.

It also allows for writing fast notes into a folder from the command line. The idea latter is to be able to search for some related information in this folders using LLMs

## How to make it work

Should be as simple as:

```
    ./install.sh
    source start.sh
```

## About the infrastructure

It uses a ollama docker to reply to the requests made by the agile_buddy python script.

I`m using an llama3.2 model as I was expecting to run this directly on the CPU, but probably you can find better results using larger models.

