# These use numpad notation: 
# 5=neutral, 6=forward, 4=back, 8=up, 2=down
# 3=down-forward, 1=down-back, 9=up-forward, 7=up-back

SSPD = ["360, 360"]                                                 # 720 motion (checked differently — see check_360)
SHCB = ["6", "2", "4", "6"]                                         # Half Circle Back, Forward
SQCBHCF = ["2", "1", "4", "2", "6"]
SQCF = ["2", "3", "6", "2", "3", "6"], ["2", "6", "2", "3", "6"], ["2", "3", "6", "2", "6"], ["2", "6", "2", "6"], ["6", "2", "3", "6", "2", "3", "6"], ["6", "2", "3", "6", "2", "6"], ["6", "2", "6", "2", "3", "6"], ["6", "2", "3", "2", "6"] # Quarter circle forward, Quarter circle forward               
SQCB = ["2", "1", "4", "2", "1", "4"], ["2", "4", "2", "1", "4"], ["2", "1", "4", "2", "4"], ["2", "4", "2", "4"], ["4", "2", "1", "4", "2", "1", "4"] # Quarter circle back, Quarter circle back
SPD  = "360"                                                        # 360 motion (checked differently — see check_360)
HCB  = ["6", "2", "4"]                                              # Half circle back
HCF  = ["4", "2", "6"]                                              # Half circle forward
RDP  = ["4", "2", "1"], ["4", "2", "4"], ["4", "2", "1", "4"]       # Reverse dragon punch
DP   = ["6", "2", "3"], ["6", "2", "6"], ["6", "2", "3", "6"]       # Dragon punch (forward, down, down-forward)
QCB  = ["2", "1", "4"]                                              # Quarter circle back
QCF  = ["2", "3", "6"]                                              # Quarter circle forward
