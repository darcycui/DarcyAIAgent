import gradio as gr
from gradio import Interface, Blocks


def setup_ui_default(fn) -> Interface:
    """
    使用 Interface 绘制文本输入输出组件 （水平排列）
    """
    return gr.Interface(
        fn=fn,
        inputs="text",
        outputs="text",
        flagging_options=["not_good", "good", "very_good"],
        submit_btn="提交",
        clear_btn="清空",
        stop_btn="停止",
        title="DarcyAiAgent"
    )

def setup_ui_vertical(fn) -> Blocks:
    """
    使用 Blocks 实现自定义布局（输入输出组件 垂直排列）
    """
    with gr.Blocks(title="DarcyAiAgent") as demo:
        # 标题
        gr.Markdown(
            """
            # 🤖 Darcy AI Agent
            智能对话助手
            """
        )

        # 主容器 - 垂直布局
        with gr.Column(scale=1):
            # 输入区域（上方）
            gr.Markdown("### 💬 输入")
            input_text = gr.Textbox(
                label="问题",
                placeholder="请输入你的问题...",
                lines=3,
                container=True
            )

            # 按钮区域
            with gr.Row():
                submit_btn = gr.Button("📤 提交 (Shift+回车)", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ 清空", size="lg")
                stop_btn = gr.Button("⏹️ 停止", size="lg")

            # 输出区域（下方）
            gr.Markdown("### 📝 输出")
            output_text = gr.Textbox(
                label="回答",
                lines=15,
                interactive=False,
                container=True,
            )

            # 反馈区域
            gr.Markdown("### 👍 反馈")
            feedback_radio = gr.Radio(
                choices=["差", "一般", "好"],
                label="评价本次回答",
                interactive=True
            )

        # 绑定事件
        submit_btn.click(
            fn=fn,
            inputs=input_text,
            outputs=output_text
        )

        # 支持按 Enter 键提交
        input_text.submit(
            fn=fn,
            inputs=input_text,
            outputs=output_text
        )

        # 清空按钮
        clear_btn.click(
            fn=lambda: ("", ""),
            inputs=None,
            outputs=[input_text, output_text]
        )

    # 返回构建好的 Blocks 实例
    return demo