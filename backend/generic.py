import re
def get_str_from_food_dict(food_dict:dict):
    result=", ".join(f"{int(v)} {k}" for k, v in food_dict.items())
    return result
def extract_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string
    return ""

#if __name__=="__main__":

    #print(extract_session_id("projects/yumgo-jqhb/agent/sessions/0b36ffce-ff48-0634-e753-98fe41813eac/contexts/ongoing-order"))