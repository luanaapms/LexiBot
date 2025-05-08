import gradio as gr
import traceback

class GradioUI:
    def __init__(self, agent):
        self.agent = agent

    def respond(self, user_input):
        try:
            response = self.agent.run({"input": user_input})
            if isinstance(response, dict) and "output" in response:
                return response["output"]
            return str(response)
        except Exception as e:
            traceback.print_exc()
            return f"Erro ao processar: {str(e)}"

    def launch(self):
        with gr.Blocks() as interface:
            gr.Markdown("# 🤖 LexiBot ")
            with gr.Row():
                with gr.Column():
                    input_box = gr.Textbox(
                        label="Digite seu texto para correção",
                        placeholder="Escreva aqui...",
                        lines=5
                    )
                    submit_btn = gr.Button("Enviar")
                with gr.Column():
                    output_box = gr.Textbox(
                        label="Resposta do agente",
                        lines=20,
                        interactive=False
                    )
            submit_btn.click(fn=self.respond, inputs=input_box, outputs=output_box)
        interface.launch()
