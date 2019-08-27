import sys
import os
sys.path.append(os.getcwd()+'/dtos')
sys.path.append(os.getcwd()+'/server')
import server.JiraFlask as server

if __name__ == '__main__':
    server.run()

