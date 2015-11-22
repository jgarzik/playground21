import sys
import json
import os

# import from the 21 Developer Library
from two1.commands.config import Config
from two1.lib.wallet import Wallet
from two1.lib.bitrequests import BitTransferRequests

# set up bitrequest client for BitTransfer requests
wallet = Wallet()
username = Config().username
requests = BitTransferRequests(wallet, username)

# server address
def buy_file(server_url = 'http://localhost:5000/'):

    # get the file listing from the server
    response = requests.get(url=server_url+'files')
    file_list = json.loads(response.text)

    # print the file list to the console
    for file in range(len(file_list)):
        print("{}. {}\t{}".format(file+1, file_list[str(file+1)][0], file_list[str(file+1)][1]))

    try:
        # prompt the user to input the index number of the file to be purchased
        sel = input("Please enter the index of the file that you would like to purchase:")

        # check if the input index is valid key in file_list dict
        if sel in file_list:
            print('You selected {} in our database'.format(file_list[sel][0]))

            #create a 402 request with the server payout address
            sel_url = server_url+'buy?selection={0}&payout_address={1}'
            answer = requests.get(url=sel_url.format(int(sel), wallet.get_payout_address()), stream=True)
            if answer.status_code != 200:
                print("Could not make an offchain payment. Please check that you have sufficient balance.")
            else:
                # open a file with the same name as the file being purchased and stream the data into it.
                filename = file_list[str(sel)][0]
                with open(filename,'wb') as fd:
                    for chunk in answer.iter_content(4096):
                        fd.write(chunk)
                fd.close()
                print('Congratulations, you just purchased a file for bitcoin!')
        else:
            print("That is an invalid selection.")

    except ValueError:
        print("That is an invalid input. Only numerical inputs are accepted.")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    else:
        server_url = 'http://localhost:5000/'
    buy_file(server_url)