import socket

# define global variables
requestIndices = list()
requestData = list()
responseIndices = list()
responseData = list()
responseMessage = ""
summationResult = 0
# socket variables
HOST = "127.0.0.1"
SELF_PORT = 8080
# define server socket
try:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((HOST, SELF_PORT))
except Exception as e:
    print(str(e))
    print("Error occured while creating the backend server socket")
    exit(1)
print("Backend server is running on {0}:{1}\n".format(HOST, SELF_PORT))
try:
    serverSocket.listen(1)
    print("Listening for connections")
except Exception as e:
    print(str(e))
    print("Error occured while listening for connections")
    exit(1)
try:
    proxyConnection, proxyAddress = serverSocket.accept()
    print("Connected by", proxyAddress)
except Exception as e:
    print(str(e))
    print("Error occured while accepting the connection")
    exit(1)

# backend server table
# serverStorage = [None, None, None, None, None, None, None, None, None, None]
serverStorage = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]


def decompose_message(message):
    global requestIndices
    global requestData
    # split the message into parts
    operation = ""
    messageParts = message.split(";")
    try:
        for mPart in messageParts:
            key, value = mPart.split("=")
            # extract the operation
            if key == "OP":
                operation = value
            # extract the indices
            elif key == "IND":
                requestIndices = [int(i) for i in value.split(",")]
            # extract the data
            elif key == "DATA":
                requestData = [int(i) for i in value.split(",")]
    except:
        print("Error occured while decomposing the message")
        raise Exception("500-Error occured while decomposing the message")
    return operation


def prepare_response_message(operation):
    global responseMessage
    global responseIndices
    global responseData
    if operation == "GET":
        responseMessage = "OP=GET;IND={0};DATA={1};CODE=200".format(
            ",".join(str(i) for i in responseIndices), ",".join(str(i) for i in responseData)
        )
    elif operation == "PUT":
        responseMessage = "OP=PUT;IND={0};DATA={1};CODE=200".format(
            ",".join(str(i) for i in requestIndices), ",".join(str(i) for i in responseData)
        )
    elif operation == "CLR":
        responseMessage = "OP=CLR;CODE=200"
    elif operation == "ADD":
        responseMessage = "OP=ADD;IND={0};DATA={1};CODE=200".format(
            ",".join(str(i) for i in requestIndices), summationResult
        )


def send_message_to_proxy():
    global responseMessage
    try:
        proxyConnection.send(responseMessage.encode("utf-8"))
        print("Sent message to the proxy: {0}".format(responseMessage))
    except:
        print("Error occured while sending message to proxy")
        raise Exception("500-Error occured while sending message to proxy")


def perform_operation(operation):
    global serverStorage
    global requestIndices
    global requestData
    global responseIndices
    global responseData
    global summationResult
    if operation == "GET":
        for index in requestIndices:
            if serverStorage[index] is None:
                raise Exception("404-Index not found")
            else:
                responseIndices.append(index)
                responseData.append(serverStorage[index])
    elif operation == "PUT":
        for index, data in zip(requestIndices, requestData):
            serverStorage[index] = data
            responseIndices.append(index)
            responseData.append(data)
        print_server_table()
    elif operation == "CLR":
        for index in range(len(serverStorage)):
            serverStorage[index] = None
        print("Server table cleared\n")
    elif operation == "ADD":
        for index in requestIndices:
            if serverStorage[index] is None:
                raise Exception("404-Index not found")
            else:
                summationResult += serverStorage[index]


def print_server_table():
    print("\nChanges made to the server table:")
    print("Index\tData")
    for i in range(len(serverStorage)):
        if serverStorage[i] is None:
            print("{0}\tNone".format(i))
        else:
            print("{0}\t{1}".format(i, serverStorage[i]))
    print("\n")


def clear_variables():
    global requestIndices
    global requestData
    global responseIndices
    global responseData
    global responseMessage
    global summationResult
    requestIndices = []
    requestData = []
    responseIndices = []
    responseData = []
    responseMessage = ""
    summationResult = 0


def main():
    global serverSocket
    global proxyConnection
    global proxyAddress
    global responseMessage
    while True:
        try:
            dataReceived = proxyConnection.recv(1024)
        except:
            print(proxyAddress, "disconnected")
            serverSocket.listen(1)
            proxyConnection, proxyAddress = serverSocket.accept()
            print("Connected by", proxyAddress)
            continue
        if dataReceived:
            try:
                dataReceived = dataReceived.decode("utf-8")
            except:
                print("Error occured while decoding the message")
                responseMessage = "CODE=500"
                try:
                    send_message_to_proxy()
                except:
                    pass
                clear_variables()
                continue
            print("Received message from proxy server: {0}".format(dataReceived))
            try:
                operation = decompose_message(dataReceived)
                perform_operation(operation)
                prepare_response_message(operation)
                send_message_to_proxy()
                print("\n")
            except Exception as e:
                print(str(e))
                print("\n")
                if "404" in str(e):
                    responseMessage = "CODE=404"
                if "500" in str(e):
                    responseMessage = "CODE=500"
                try:
                    send_message_to_proxy()
                except:
                    pass
            clear_variables()


if __name__ == "__main__":
    main()
