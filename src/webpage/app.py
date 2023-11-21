from pathlib import Path

import gradio as gr
import pyonmttok
import torch.jit

model = None
tokenizer = None
lang_enum = None

TITLE = "Tglang: Programming Language Detection"
DESCRIPTION = ("<h5 style=\"text-align:center\">"
               "Enter a code snippet and the model will predict the programming language it is written in.\n\n"
               "Alternatively, it's possible to select one example from the dropdown menu to see how the model works.<h5>")
FOOTER = ("This is a solution for the "
            "[Telegram ML competition 2023, Round 2](https://contest.com/docs/ML-Competition-2023-r2).\n\n"
          "For more details, read [this article]() or check out [this repo]()")
EXAMPLES = [
    ["def foo():\n    print('Hello, world!')", "TGLANG_LANGUAGE_PYTHON"],
    ["int main() {\n    printf(\"Hello, world!\");\n    return 0;\n}", "TGLANG_LANGUAGE_C"],
    ["function foo() {\n    console.log('Hello, world!');\n}", "TGLANG_LANGUAGE_JAVASCRIPT"],
    ["public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, world!\");\n    }\n}", "TGLANG_LANGUAGE_JAVA"],
    ["#include <iostream>\n\nint main() {\n    std::cout << \"Hello, world!\" << std::endl;\n}", "TGLANG_LANGUAGE_CPP"],
    ["using System;\n\npublic class Program\n{\n    public static void Main()\n    {\n        Console.WriteLine(\"Hello, world!\");\n    }\n}", "TGLANG_LANGUAGE_CSHARP"],
]


def init_model():
    global model, tokenizer, lang_enum
    tokenizer = pyonmttok.Tokenizer("conservative")
    model = torch.jit.load(Path(__file__).with_name("tglang.pt"))
    lang_enum = Path(__file__).with_name("langs_enum_r2.txt").read_text().strip().split("\n")
    lang_enum = [l.strip() for l in lang_enum if bool(l)]


def predict(text):
    global model, tokenizer, lang_enum
    tokens = tokenizer(text)
    lang_index, *_ = model([tokens])
    return lang_enum[lang_index]


def create_demo():
    init_model()
    demo = gr.Interface(fn=predict,
                        inputs=gr.Textbox(label="Code snippet", placeholder="Enter code here..."),
                        outputs=gr.Textbox(label="Model prediction"),
                        title=TITLE,
                        description=DESCRIPTION,
                        examples=EXAMPLES,
                    theme=gr.themes.Monochrome(),
                        article=FOOTER,
                        )
    return demo


demo = create_demo()


if __name__ == "__main__":
    demo.launch(show_api=False)
