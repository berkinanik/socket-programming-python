# import necessary libraries
import socket
from time import sleep


# define global variables
specifiedIndices = list()
specifiedData = list()
responseIndices = list()
responseData = list()
message = ""
responseMessage = ""
# socket variables
HOST = "127.0.0.1"
PROXY_PORT = 8081
# define the client socket
try:
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Client socket created successfully\n")
except Exception as e:
    print(str(e))
    print("Error occured while creating the client server socket")
    exit(1)
try:
    clientSocket.connect((HOST, PROXY_PORT))
    print("Connected to the proxy server at {0}:{1}\n".format(HOST, PROXY_PORT))
except Exception as e:
    print(str(e))
    print("Error occured while connecting to the proxy server")
    exit(1)


# function for getting parameters required for the get or add operation
def get_or_add_operation_prompt(operation):
    # operation is either get or add
    # if operation is 1, get operation
    # if operation is 4, add operation
    # check if operation is valid
    if operation == 1 or operation == 4:
        pass
    else:
        raise Exception("Invalid operation mode ({0}) supplied to get_or_add_operation_prompt.".format(operation))
    global specifiedIndices
    enteredIndices = input(
        "Enter the indices you want to {0}:\n(format required is: 0,1,2,3,4,5,... [indices between 0-9])\n".format(
            "get" if operation == 1 else "add"
        )
    )
    specifiedValidIndices = list()
    try:
        enteredIndices = enteredIndices.strip(" ").replace(" ", "").split(",")
        for index in enteredIndices:
            if int(index) < 0 or int(index) > 9:
                raise ValueError("Invalid index: {0}. Try again\n".format(index))
            specifiedValidIndices.append(int(index))
        if operation == 4 and (len(specifiedValidIndices) < 2 or len(specifiedValidIndices) > 5):
            raise ValueError(
                "At least 2 indices needed and maximum of 5 indices are allowed for add operation. Try again\n"
            )
        # assign the indices to the global variable
        specifiedIndices = specifiedValidIndices
    except ValueError as e:
        raise e
    except:
        # raise error if the input is not valid
        raise ValueError("Invalid input. Try again\n")


# function for getting parameters required for the put operation
def put_operation_prompt():
    global specifiedIndices
    global specifiedData
    enteredIndices = input(
        "Enter the indices you want to put:\n(format required is: 0,1,2,3,4,5,... [indices between 0-9])\n"
    )
    enteredData = input(
        "Enter the data you want to put:\n(format required is: 11,111,0,-3,41,50,... [data format integer])\n"
    )
    specifiedValidIndices = list()
    specifiedValidData = list()
    try:
        enteredIndices = enteredIndices.strip(" ").replace(" ", "").split(",")
        enteredData = enteredData.strip(" ").replace(" ", "").split(",")
        for index in enteredIndices:
            if int(index) < 0 or int(index) > 9:
                raise ValueError("Invalid index: {0}. Try again\n".format(index))
            specifiedValidIndices.append(int(index))
        for datum in enteredData:
            specifiedValidData.append(int(datum))
        if len(specifiedValidIndices) != len(specifiedValidData):
            raise ValueError("Invalid data: Entered indices and data length does not match. Try again")
        specifiedData = specifiedValidData
        specifiedIndices = specifiedValidIndices
    except ValueError as e:
        raise e
    except:
        raise ValueError("Invalid input. Try again\n")


# function to prepare the message to be sent to the proxy server
def prepare_message(operation):
    global message
    if operation == 1:
        message = "OP=GET;IND={0}".format(",".join(str(i) for i in specifiedIndices))
    elif operation == 2:
        message = "OP=PUT;IND={0};DATA={1}".format(
            ",".join(str(i) for i in specifiedIndices), ",".join(str(i) for i in specifiedData)
        )
    elif operation == 3:
        message = "OP=CLR"
    elif operation == 4:
        message = "OP=ADD;IND={0}".format(",".join(str(i) for i in specifiedIndices))


# function to send the message to the proxy server
def send_message_to_proxy():
    global message
    global clientSocket
    clientSocket.send(message.encode())
    print("Message sent to proxy server: {0}\n".format(message))


# function to decompose the server response
def decompose_message():
    global responseMessage
    global responseIndices
    global responseData
    # split the message into parts
    operation = ""
    messageParts = responseMessage.split(";")
    try:
        for mPart in messageParts:
            key, value = mPart.split("=")
            # extract the operation
            if key == "OP":
                operation = value
            # extract the indices
            elif key == "IND":
                responseIndices = [int(i) for i in value.split(",")]
            # extract the data
            elif key == "DATA":
                responseData = [int(i) for i in value.split(",")]
            elif key == "CODE":
                if int(value) == 404:
                    raise Exception("Requested indices not found. Try again")
                elif int(value) == 500:
                    raise Exception("Server error. Try again")
                elif int(value) == 200:
                    pass
    except Exception as e:
        raise e
    return operation


# function to print the server response
def print_response(operation):
    global responseIndices
    global responseData
    if operation == "GET":
        print("Retrieved data\nIndex\tData")
        for i in range(len(responseIndices)):
            print("{0}\t{1}".format(responseIndices[i], responseData[i]))
    elif operation == "PUT":
        print("Updated data\nIndex\tData")
        for i in range(len(responseIndices)):
            print("{0}\t{1}".format(responseIndices[i], responseData[i]))
    elif operation == "CLR":
        print("Cleared data")
    elif operation == "ADD":
        print("Added indexes: {0}".format(",".join(str(i) for i in responseIndices)))
        print("Summation Result: {0}".format(responseData[0]))


# function to clear variables
def clear_variables():
    global specifiedIndices
    global specifiedData
    global responseIndices
    global responseData
    global message
    global responseMessage
    responseMessage = ""
    message = ""
    specifiedIndices = []
    specifiedData = []
    responseIndices = []
    responseData = []


# function for the client interface
def main():
    global message
    global specifiedData
    global specifiedIndices
    global responseMessage
    global clientSocket
    while 1:
        # first list available operations
        print("Available operations:")
        print("1. GET: (type 1)")
        print("2. PUT: (type 2)")
        print("3. CLR: (type 3)")
        print("4. ADD: (type 4)")
        print("5. Exit: (type 5)")
        # prompt the user for the operation
        chosenOperation = input("\nEnter the operation you want to perform:\n")
        # check if the operation is valid
        try:
            chosenOperation = int(chosenOperation)
        except:
            print("Invalid operation. Try again\n")
            sleep(1)
            continue
        if chosenOperation < 1 or chosenOperation > 5:
            print("Invalid operation. Try again\n")
            sleep(1)
            continue
        else:
            # operation is valid as for required parameters for operation
            # get the parameters from the user
            # send the message to the server
            # wait for the response from the server
            # print the response
            # clear the global variables
            try:
                if chosenOperation == 5:
                    print("\nExiting...\n")
                    break
                elif chosenOperation == 1:
                    get_or_add_operation_prompt(1)
                elif chosenOperation == 2:
                    put_operation_prompt()
                elif chosenOperation == 4:
                    get_or_add_operation_prompt(4)
                else:
                    pass
                prepare_message(chosenOperation)
                print("\nSending message to the server...")
                send_message_to_proxy()
                try:
                    dataReceived = clientSocket.recv(1024)
                except:
                    print("\nError occurred while receiving data from the proxy server.\n")
                    print("Exiting...\n")
                    exit(1)
                if dataReceived:
                    try:
                        responseMessage = dataReceived.decode("utf-8")
                    except:
                        print("Error occured while decoding the message")
                        continue
                    print("\nReceived message from the proxy server: {0}".format(responseMessage))
                    try:
                        operation = decompose_message()
                        print_response(operation)
                    except Exception as e:
                        print(str(e))
                    clear_variables()
                    print("\n")
                    sleep(1)
            except Exception as e:
                print(e)
                sleep(1)
                continue


if __name__ == "__main__":
    main()
