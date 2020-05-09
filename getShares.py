# Returns a dictionary of 401K {symbols: shares} from a specific Google Sheets spreadsheet
# Module for use in av_portfolio.py program
# If run directly from the command line it will store the shares as a JSON dictionary in shares.txt
# James S. Lucas - 20190511

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():
   pass

def getShares():
   scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
   credentials = ServiceAccountCredentials.from_json_keyfile_name('JSL Python Sheets-450059ada1ac.json', scope)
   gc = gspread.authorize(credentials)
   sheet_title = '401K'

   wks = gc.open('401K Portfolio Data').worksheet(sheet_title)

   symbol_shares = 0.0
   ticker_symbols = ['FSKAX','FSMAX','FSPSX','FXAIX','FXNAX','VTI','VBTLX','VIPSX','VTSAX']
   shares = {'FSKAX': 0.0,'FSMAX': 0.0,'FSPSX': 0.0,'FXAIX': 0.0,'FXNAX': 0.0,'VTI': 0.0,'VBTLX': 0.0,'VIPSX': 0.0,'VTSAX': 0.0, 'BND': 0.0}

   for ticker_symbol in ticker_symbols:
      symbol_cells = wks.findall(ticker_symbol)
      if type(symbol_cells) is list: #multiple cells match ticker_symbol
         for cell in symbol_cells: #loop over the cells and aggregate the number of shares for the symbol
            symbol_shares = symbol_shares + float(wks.cell(cell.row,8).value)
      else:
         symbol_shares = wks.cell(symbol_cells.row,8).value
      shares[ticker_symbol] = symbol_shares #update the shares dictionary with the number of shares for the ticker_symbol
      symbol_shares = 0.0

   #print " "
   #print "Shares"
   #print shares
   #print " "

   return shares

if __name__ == "__main__":
   # This won't be run when imported
   import json
   shares = getShares()
   json.dump(shares, open("shares.txt",'w')) #write the shares dictionary to a text file

