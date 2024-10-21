---
license: odc-by
tags:
- code
---

The Sketch2Code dataset consists of 731 human-drawn sketches paired with 484 real-world webpages from the [Design2Code dataset](https://huggingface.co/datasets/SALT-NLP/Design2Code), serving to benchmark Vision-Language Models (VLMs) on converting rudimentary sketches into web design prototypes.

Each example consists of a pair of source HTML and rendered webpage screenshot (stored in `webpages/` directory under name `{webpage_id}.html` and `{webpage_id}.png`), as well as 1 to 3 sketches drawn by human annotators (stored in `sketches/` directory under name {webpage_id}_{sketch_id}.png).

Note that all images in these webpages are replaced by a blue placeholder image (rick.jpg).

Please refer to our [Project Page](https://salt-nlp.github.io/Sketch2Code-Project-Page/) for more detailed information.