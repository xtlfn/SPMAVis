import streamlit as st

# 设置应用标题
st.title("简单的 Streamlit WebApp")

# 添加输入框和按钮
name = st.text_input("请输入你的名字：")
if st.button("提交"):
    st.write(f"你好，{name}！欢迎使用 Streamlit 应用。")
else:
    st.write("请在上方输入框输入名字，然后点击“提交”。")

# 显示示例图片
st.image("static/image.png", caption="示例图片", use_column_width=True)