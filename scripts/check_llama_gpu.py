try:
    import llama_cpp
    print(llama_cpp.get_system_info())
except Exception as e:
    print(e)
