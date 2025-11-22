import os
import gradio as gr
from tqdm import tqdm

import modules.scripts as scripts
import modules.sd_samplers_common as sd
from modules.script_callbacks import on_cfg_denoiser, remove_current_script_callbacks
from modules.shared import state

class Script(scripts.Script):

    def title(self):
        return "autoSkip"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("autoSkip", open=True, elem_id="autoskip"):                                                          
            with gr.Row(equal_height=True):
                with gr.Column(scale=100):
                    autoskip_slider = gr.Slider(minimum=0.00, maximum=1.00, step=.05, value=0.00, label="Skip", interactive=True, elem_id="autoskip-slider")
                with gr.Column(scale=1, min_width=120):
                    with gr.Row():
                        autoskip_input = gr.Number(value=0.00, precision=4, label="Skip", show_label=False, elem_id="autoskip-number")   
                        reset_but = gr.Button(value='✕', elem_id='autoskip-x', size='sm')           

            js = """(v) => {
              ['#tab_txt2img #autoskip-x', '#tab_img2img #autoskip-x'].forEach((selector, index) => {
                const element = document.querySelector(selector);
                if (document.querySelector(`#tab_${index ? 'img2img' : 'txt2img'}`).style.display === 'block') {
                  element.style.cssText += `outline:4px solid rgba(255,86,0,${Math.sqrt(v)}); border-radius: 0.4em !important;`;
                }
              });
              return v;
            }"""
               
            autoskip_input.change(None, [autoskip_input], autoskip_slider, _js=js)
            autoskip_slider.release(None, autoskip_slider, autoskip_input, _js="(x) => x")
            reset_but.click(None, [], [autoskip_input,autoskip_slider], _js="(x) => [0,0]")

        self.infotext_fields = []        
        self.infotext_fields.extend([
            (autoskip_input, "autoSkip")
        ])
        self.paste_field_names = []
        for _, field_name in self.infotext_fields:
            self.paste_field_names.append(field_name)

        return [autoskip_input]
    

    def process(self, p, autoskip):
        autoskip = getattr(p, 'autoSkip', autoskip)
        self.autoskip = autoskip
        self.counter = 0
        if hasattr(self, 'callbacks_added'):
            remove_current_script_callbacks()
            delattr(self, 'callbacks_added')
            # tqdm.write('autoSkip callback removed')

        if self.autoskip > 0:
            self.print_warning(autoskip) 
            on_cfg_denoiser(self.denoise_callback)
            self.callbacks_added = True
            # tqdm.write('autoSkip callback added') 

            p.extra_generation_params.update({
                "autoSkip": self.autoskip,
            })

    def postprocess(self, p, processed, *args):
        if hasattr(self, 'callbacks_added'):
            remove_current_script_callbacks()
            delattr(self, 'callbacks_added')
            # tqdm.write('autoSkip callback removed') 

    def denoise_callback(self, params):    
        # tqdm.write(f"Actual Step: {self.counter}")
        if self.autoskip is not None and self.counter >= (1 - self.autoskip) * state.sampling_steps:
            tqdm.write(f"\033[95mINFO:\033[0m Skipped at step {self.counter}")
            self.counter = 0
            raise sd.InterruptedException            
        self.counter += 1

    def print_warning(self, value):
        if value == 0:
            return
        color_code = '\033[95m'   
        tqdm.write(f"\n{color_code}ATTENTION:\033[0m autoSkip is set to {value}")            
