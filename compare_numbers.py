def compare_numbers():
    """3.12と3.8を比較する関数"""
    num1 = 3.12
    num2 = 3.8
    
    print(f"数値の比較: {num1} と {num2}")
    print(f"num1 = {num1}")
    print(f"num2 = {num2}")
    
    if num1 > num2:
        print(f"結果: {num1} は {num2} より大きいです")
        result = f"{num1} > {num2}"
    elif num1 < num2:
        print(f"結果: {num1} は {num2} より小さいです")
        result = f"{num1} < {num2}"
    else:
        print(f"結果: {num1} と {num2} は等しいです")
        result = f"{num1} = {num2}"
    
    return result

if __name__ == "__main__":
    result = compare_numbers()
    print(f"\n最終結果: {result}")