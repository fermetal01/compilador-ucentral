from compiler import pi

while True:
    text = input('pi > ')
    result, error = pi.run('<stdin>', text)
    if error:
        print(error.as_string())
    else:
        print(result)
