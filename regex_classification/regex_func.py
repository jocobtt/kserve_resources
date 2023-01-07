import re 
import pickle

def regex_func(regex, string):
    # compile our regex
    #pattern = re.compile(regex)
    if re.match(regex, string):
        return True
    else:
        return False

# now convert the function to dump file 
with open("regex_dump.pkl", "wb") as f:
    pickle.dump(regex_func, f)
#dump(reg_func, "regex_dump.joblib")

if __name__ == "__main__":
    if regex_func(r"\d+", "7"):
        print("the string matches the pattern")
    else:
        print("the string does not match the pattern")
    print("done")
