import concurrent.futures, csv, gc, glob, hashlib, importlib, itertools, logging, os, platform, re, shutil, subprocess, sys, textwrap, threading, time, urllib.request, urllib.error, zipfile
from datetime import datetime, timedelta
from queue import PriorityQueue, Empty, Queue
from threading import Lock
from zipfile import ZipFile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from urllib.error import HTTPError, URLError

# Native Python modulesss
native_modules = [
    'csv', 'gc', 'glob', 'hashlib', 'itertools', 'logging', 'os', 're', 'shutil', 
    'sys', 'textwrap', 'threading', 'time', 'urllib.request', 'urllib.error', 'zipfile',
    'datetime', 'queue', 'pathlib'
]

# Non-native Python modules for third-party installation
third_party_modules = [
    'chardet', 'pandas', 'requests', 'bs4', 'tqdm'
]
# Constants
ROOT_DIR = "./"
FILELIST = os.path.join(ROOT_DIR, "filelist.txt")
FORMD_SOURCE_DIR = os.path.join(ROOT_DIR, "SecFormD")
NCEN_SOURCE_DIR = os.path.join(ROOT_DIR, "SecNcen")
NPORT_SOURCE_DIR = os.path.join(ROOT_DIR, "SecNport")
THRTNF_SOURCE_DIR = os.path.join(ROOT_DIR, "Sec13F")
NMFP_SOURCE_DIR = os.path.join(ROOT_DIR, "SecNmfp")
CREDIT_SOURCE_DIR = os.path.join(ROOT_DIR, "CREDITS")
EQUITY_SOURCE_DIR = os.path.join(ROOT_DIR, "EQUITY")
CFTC_EQUITY_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_EQ")
CFTC_CREDIT_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_CR")
CFTC_COMMODITIES_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_CO")
CFTC_FOREX_SOURCE_DIR = os.path.join(ROOT_DIR, "FOREX")
CFTC_RATES_SOURCE_DIR = os.path.join(ROOT_DIR, "CFTC_IR")
EDGAR_SOURCE_DIR = os.path.join(ROOT_DIR, "EDGAR")
EXCHANGE_SOURCE_DIR = os.path.join(ROOT_DIR, "EXCHANGE")
INSIDER_SOURCE_DIR = os.path.join(ROOT_DIR, "INSIDERS")
directories = [
    INSIDER_SOURCE_DIR,
    EXCHANGE_SOURCE_DIR,
    EDGAR_SOURCE_DIR,
    EQUITY_SOURCE_DIR,
    CREDIT_SOURCE_DIR,
    CFTC_CREDIT_SOURCE_DIR,
    CFTC_EQUITY_SOURCE_DIR,
    CFTC_COMMODITIES_SOURCE_DIR,
    CFTC_FOREX_SOURCE_DIR,
    CFTC_RATES_SOURCE_DIR,
    NMFP_SOURCE_DIR,
    THRTNF_SOURCE_DIR,
    NPORT_SOURCE_DIR,
    NCEN_SOURCE_DIR,
    FORMD_SOURCE_DIR,
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_and_install_modules():
    os_name = platform.system()

    if os_name == "Linux":
        # Install pip if not already installed
        try:
            subprocess.check_call(["sudo", "apt", "-qq", "-y", "install", "python3-pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("Failed to install pip. Ensure you have sudo privileges.")

    # For Windows and macOS, we'll rely on pip for Python packages

    for module in third_party_modules:
        try:
            importlib.import_module(module.replace('.', '_'))  # Handle modules with dots in name
            print(f"{module} is already installed.")
        except ImportError:
            print(f"{module} is not installed.")
            pip_command = [sys.executable, '-m', 'pip', 'install', module]
            try:
                subprocess.check_call(pip_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"{module} installed successfully.")
            except subprocess.CalledProcessError:
                print(f"Failed to install {module}. Please install it manually.")
def import_modules():
    global chardet, concurrent, requests, BeautifulSoup, tqdm, pd

    # Third-party modules
    import chardet
    import concurrent.futures as concurrent
    import requests
    from bs4 import BeautifulSoup
    from tqdm import tqdm
    import pandas as pd

    # Specific imports from concurrent.futures
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
def gamecock_ascii():
    print(r"""
                                                  __    
   _________    _____   ____   ____  ____   ____ |  | __
  / ___\__  \  /     \_/ __ \_/ ___\/  _ \_/ ___\|  |/ /W
 / /_/  > __ \|  Y Y  \  ___/\  \__(  <_> )  \___|    < 
 \___  (____  /__|_|  /\___  >\___  >____/ \___  >__|_ |
/_____/     \/      \/     \/     \/           \/     \|
""")
def gamecat_ascii():
    print(r"""
     _         /\_/\
    ( \       /    `\
     ) )   __|   G G| 
    / /  /`   `'.= Y)= 
   ( (  /        `"`} 
    \ \|    \       }
     \ \     ),   //
     '._,  /'-\ ( (
         \, ,))\,),)
        ASBT SAYS GAME ON.
    """)
def codex():
    """Introductory function to clear the screen, display ASCII art, and prompt the user."""
    # ANSI escape codes for colors
    COLORS = [
        '\033[31m',  # Red
        '\033[33m',  # Yellow
        '\033[32m',  # Green
        '\033[36m',  # Cyan
        '\033[34m',  # Blue
        '\033[35m',  # Magenta
    ]

    RESET = '\033[0m'  # Reset to default color

    def colorize_text(text):
        """Colorize the text with a rainbow gradient."""
        color_cycle = itertools.cycle(COLORS)
        colored_text = ''
        for char in text:
            if char == '\n':
                colored_text += char
            else:
                colored_text += next(color_cycle) + char
        return colored_text + RESET

    def get_terminal_width():
        """Get the current width of the terminal window."""
        try:
            # Get terminal size (columns, lines)
            columns, _ = os.get_terminal_size()
        except AttributeError:
            # Default width if os.get_terminal_size() is not available (e.g., on Windows)
            columns = 80
        return columns

    def display_text_normally(text, width=80):
        """Display the given text with word wrap and ensure newlines are preserved."""
        # Split the text into lines and handle each line individually
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            # Wrap each line of text
            wrapped_lines.append(textwrap.fill(line, width=width))
        
        # Join the wrapped lines back together with newlines in between
        wrapped_text = '\n'.join(wrapped_lines)
        print(wrapped_text)

    def display_hardcoded_ascii_art():
        """Display hardcoded ASCII art with rainbow gradient."""
        ascii_art = """\
mmmmmmm m    m mmmmmm          mmm   mmmm  mmmm   mmmmmm m    m
   #    #    # #             m"   " m"  "m #   "m #       #  # a
   #    #mmmm# #mmmmm        #      #    # #    # #mmmmm   ##  
   #    #    # #             #      #    # #    # #       m""m 
   #    #    # #mmmmm         "mmm"  #mm#  #mmm"  #mmmmm m"  "m
"""
        print(colorize_text(ascii_art))
        time.sleep(3)  # Show for 3 seconds

    def prompt_user():
        """Prompt the user to choose between learning SEC forms, Market Instruments, or quitting."""
        while True:
            print("\nPlease choose an option:")
            print("1. Learn about SEC forms pt. 6")
            print("2. Learn about SEC forms pt. 9")
            print("3. Learn about Market Instruments pt. 420")
            print("Q. Quit")

            choice = input("Enter 1, 2, or Q: ").strip().lower()
            
            if choice == '1' or choice == 'sec forms':
                text_content ="""
1. 10-K
   - Description: The 10-K is an annual report filed by publicly traded companies to provide a comprehensive overview of the company's financial performance. It includes audited financial statements, management discussion and analysis, and details on operations, risk factors, and governance.
   - Investopedia Link: https://www.investopedia.com/terms/1/10-k.asp

2. 10-K/A
   - Description: The 10-K/A is an amendment to the annual 10-K report. It is used to correct or update information that was originally filed in the 10-K.
   - Investopedia Link: https://www.investopedia.com/terms/1/10-k.asp

3. 10-Q
   - Description: The 10-Q is a quarterly report that companies must file after the end of each of the first three quarters of their fiscal year. It provides an update on the company's financial performance, including unaudited financial statements and management discussion.
   - Investopedia Link: https://www.investopedia.com/terms/1/10-q.asp

4. 10-Q/A
   - Description: The 10-Q/A is an amendment to the quarterly 10-Q report. It is used to correct or update information that was originally filed in the 10-Q.
   - Investopedia Link: https://www.investopedia.com/terms/1/10-q.asp

5. 8-K
   - Description: The 8-K is used to report major events or corporate changes that are important to shareholders. These events can include mergers, acquisitions, bankruptcy, or changes in executives.
   - Investopedia Link: https://www.investopedia.com/terms/1/8-k.asp

6. 8-K/A
   - Description: The 8-K/A is an amendment to the 8-K report. It is filed to provide additional information or correct information originally reported in an 8-K.
   - Investopedia Link: https://www.investopedia.com/terms/1/8-k.asp

7. DEF 14A
   - Description: The DEF 14A, or Definitive Proxy Statement, provides information about matters to be voted on at a company’s annual meeting, including executive compensation, board nominees, and other significant proposals.
   - Investopedia Link: https://www.investopedia.com/terms/d/definitive-proxy-statement.asp

8. DEF 14A/A
   - Description: The DEF 14A/A is an amendment to the DEF 14A Proxy Statement. It is used to update or correct information originally filed in the DEF 14A.
   - Investopedia Link: https://www.investopedia.com/terms/d/definitive-proxy-statement.asp

9. F-1
   - Description: The F-1 is used by foreign companies seeking to list their shares on U.S. exchanges. It provides information similar to the S-1 but tailored for foreign entities.
   - Investopedia Link: https://www.investopedia.com/terms/f/f-1.asp

10. F-1/A
    - Description: The F-1/A is an amendment to the F-1 registration statement. It is used to update or correct information for foreign companies seeking to list their shares on U.S. exchanges.
    - Investopedia Link: https://www.investopedia.com/terms/f/f-1.asp

11. Form 3
    - Description: Form 3 is used by insiders of a company to report their ownership of the company's securities upon becoming an insider. It is required to be filed within 10 days of becoming an officer, director, or beneficial owner.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-3.asp

12. Form 3/A
    - Description: The Form 3/A is an amendment to the original Form 3 filing. It is used to correct or update information regarding insider ownership.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-3.asp

13. Form 4
    - Description: Form 4 is used to report changes in the holdings of company insiders. It must be filed within two business days of the transaction.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-4.asp

14. Form 4/A
    - Description: The Form 4/A is an amendment to the original Form 4 filing. It is used to correct or update information regarding changes in insider holdings.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-4.asp

15. Form 5
    - Description: Form 5 is an annual report used to disclose transactions that were not reported on Form 4, including certain gifts or changes in ownership.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-5.asp

16. Form 5/A
    - Description: The Form 5/A is an amendment to the original Form 5 filing. It is used to correct or update information about transactions not previously reported.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-5.asp

17. Form ADV
    - Description: Form ADV is filed by investment advisers to register with the SEC and state regulators. It provides details about the adviser’s business, services, and fees.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-adv.asp

18. Form ADV/A
    - Description: Form ADV/A is an amendment to the original Form ADV filing. It is used to update or correct information about investment advisers.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-adv.asp

19. Form D
    - Description: Form D is filed by companies offering securities that are exempt from registration under Regulation D. It includes information about the offering and the issuer.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-d.asp

"""
                break
            elif choice == '2' or choice == 'more sec forms':
                text_content ="""
20. Form D/A
    - Description: Form D/A is an amendment to the original Form D filing. It is used to update or correct information about securities offerings exempt from registration.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-d.asp

21. Form N-1A
    - Description: Form N-1A is used by mutual funds to register with the SEC and provide information to investors about the fund’s investment objectives, strategies, and fees.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-n-1a.asp

22. Form N-1A/A
    - Description: Form N-1A/A is an amendment to the original Form N-1A filing. It is used to update or correct information about mutual funds.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-n-1a.asp

23. Form N-CSR
    - Description: Form N-CSR is filed by registered management investment companies to report their certified shareholder reports and other important financial statements.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-n-csr.asp

24. Form N-CSR/A
    - Description: Form N-CSR/A is an amendment to the original Form N-CSR filing. It is used to update or correct information about certified shareholder reports.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-n-csr.asp

25. Form N-Q
    - Description: Form N-Q is used by investment companies to report their portfolio holdings on a quarterly basis, providing details on the investments and their values.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-n-q.asp

26. Form N-Q/A
    - Description: Form N-Q/A is an amendment to the original Form N-Q filing. It is used to update or correct information about investment company portfolio holdings.
    - Investopedia Link: https://www.investopedia.com/terms/f/form-n-q.asp

27. 13D
    - Description: Schedule 13D is filed by investors who acquire more than 5% of a company's outstanding shares. It includes information about the investor's intentions and background.
    - Investopedia Link: https://www.investopedia.com/terms/s/schedule-13d.asp

28. 13D/A
    - Description: Schedule 13D/A is an amendment to the original Schedule 13D filing. It is used to update or correct information about significant shareholders.
    - Investopedia Link: https://www.investopedia.com/terms/s/schedule-13d.asp

29. 13G
    - Description: Schedule 13G is an alternative to Schedule 13D for investors who acquire more than 5% of a company but do not intend to influence or control the company. It is typically used by passive investors.
    - Investopedia Link: https://www.investopedia.com/terms/s/schedule-13g.asp

30. 13G/A
    - Description: Schedule 13G/A is an amendment to the original Schedule 13G filing. It is used to update or correct information about passive investors who hold more than 5% of a company's shares.
    - Investopedia Link: https://www.investopedia.com/terms/s/schedule-13g.asp

31. 13F
    - Description: Form 13F is filed quarterly by institutional investment managers to disclose their holdings in publicly traded securities. It provides transparency into the investment activities of large institutional investors.
    - Investopedia Link: https://www.investopedia.com/terms/1/13f.asp

32. 13F/A
    - Description: Form 13F/A is an amendment to the original Form 13F filing. It is used to update or correct information regarding institutional investment holdings.
    - Investopedia Link: https://www.investopedia.com/terms/1/13f.asp

33. S-1
    - Description: The S-1 is a registration statement required by the SEC for companies intending to go public through an initial public offering (IPO). It includes detailed information about the company’s business model, financials, and risks.
    - Investopedia Link: https://www.investopedia.com/terms/s/s-1.asp

34. S-1/A
    - Description: The S-1/A is an amendment to the S-1 registration statement. It is used to update or correct information in the original S-1 filing.
    - Investopedia Link: https://www.investopedia.com/terms/s/s-1.asp

35. S-3
    - Description: The S-3 is a simplified registration form used by companies that already have a track record of compliance with SEC reporting requirements. It allows for faster and easier registration of securities for public sale.
    - Investopedia Link: https://www.investopedia.com/terms/s/s-3.asp

36. S-3/A
    - Description: The S-3/A is an amendment to the S-3 registration statement. It is used to update or correct information in the original S-3 filing.
    - Investopedia Link: https://www.investopedia.com/terms/s/s-3.asp

37. S-4
    - Description: The S-4 is used for registration of securities in connection with mergers, acquisitions, and other business combinations. It includes detailed information about the transaction and the companies involved.
    - Investopedia Link: https://www.investopedia.com/terms/s/s-4.asp

38. S-4/A
    - Description: The S-4/A is an amendment to the S-4 registration statement. It is used to update or correct information in the original S-4 filing.
    - Investopedia Link: https://www.investopedia.com/terms/s/s-4.asp

"""
                break
            elif choice == '3' or choice == 'market instruments':
                text_content ="""
Codex of Financial Instruments ver 1.42069

To avoid enslavement by the increasingly sophisticated and total control mechanisms outlined in the financial layers, free humans must adopt a multifaceted strategy that emphasizes education, decentralization, community resilience, regulatory reform, and technological empowerment. These moves collectively aim to empower individuals and communities, ensuring they retain autonomy and prevent the concentration of power that leads to total control.\n

    Education and Awareness: The first line of defense against financial and societal enslavement is widespread education and awareness. People need to be informed about the complex financial instruments and control mechanisms that can potentially be used against them. This includes understanding basic financial literacy, the risks and benefits of various investment products, and the implications of emerging technologies like AI, blockchain, and quantum computing. By demystifying these elements, individuals can make informed decisions and resist manipulative financial practices.\n
    Decentralization of Power: To counteract the concentration of control, promoting decentralized systems is crucial. This can be achieved through the adoption of decentralized financial technologies (DeFi), blockchain, and cryptocurrencies, which reduce reliance on centralized financial institutions and governments. Decentralized systems ensure transparency, enhance security, and empower individuals to manage their assets independently. Furthermore, supporting decentralized governance models can distribute decision-making power more evenly across society, preventing the monopolization of control by a few elites.\n
    Strengthening Community Resilience: Building strong, resilient communities is essential to withstand external pressures and maintain autonomy. This involves fostering local economies through community banking, cooperative businesses, and local investment initiatives. Communities should invest in sustainable practices, such as local food production and renewable energy, to reduce dependency on external systems. Additionally, promoting social cohesion and mutual support networks can help communities collectively resist oppressive measures and support each other in times of crisis.\n
    Advocacy for Regulatory Reform: Ensuring fair and transparent financial markets requires active advocacy for regulatory reforms. Individuals and communities must pressure governments to implement regulations that protect against financial manipulation, ensure corporate accountability, and promote transparency in all financial dealings. Strengthening anti-corruption measures and enhancing oversight of financial institutions can prevent abuses of power and protect the interests of the general public. Effective regulation can also mitigate the risks associated with advanced financial instruments and technologies.\n
    Technological Empowerment: Embracing and harnessing technology in an ethical and controlled manner can empower individuals and communities. Investing in and promoting technologies that enhance privacy, security, and autonomy is critical. This includes using secure communication tools, privacy-focused financial platforms, and ethical AI systems that prioritize human well-being. Additionally, fostering innovation in these areas can create alternatives to the centralized technologies that may be used for control. By being proactive in technological adoption and development, free humans can stay ahead of potential threats and retain their freedom.\n

1. **Level 1 Instruments**
   - **Stocks (Equities)**
     - **Common Stock**: Represents ownership in a company and constitutes a claim on part of the company's profits. Common stockholders typically have voting rights.
       - [Investopedia: Common Stock](https://www.investopedia.com/terms/c/commonstock.asp)\n
     - **Preferred Stock**: A class of ownership with a fixed dividend, usually without voting rights. Preferred stockholders have priority over common stockholders in the event of liquidation.
       - [Investopedia: Preferred Stock](https://www.investopedia.com/terms/p/preferredstock.asp)\n
   - **Government Bonds**
     - **Treasury Bills (T-Bills)**: Short-term government securities with maturities ranging from a few days to one year.
       - [Investopedia: Treasury Bills](https://www.investopedia.com/terms/t/treasurybill.asp)\n
     - **Treasury Notes (T-Notes)**: Government securities with maturities ranging from two to ten years, paying interest every six months.
       - [Investopedia: Treasury Notes](https://www.investopedia.com/terms/t/treasurynote.asp)\n
     - **Treasury Bonds (T-Bonds)**: Long-term government securities with maturities of 20 to 30 years, paying semiannual interest.
       - [Investopedia: Treasury Bonds](https://www.investopedia.com/terms/t/treasurybond.asp)\n
   - **Commodity Futures**: Contracts to buy or sell a commodity at a future date at a price agreed upon today.
     - [Investopedia: Commodity Futures](https://www.investopedia.com/terms/f/futurescontract.asp)\n
   - **Exchange-Traded Funds (ETFs)**: Investment funds traded on stock exchanges, much like stocks.
     - [Investopedia: ETF](https://www.investopedia.com/terms/e/exchange-tradedfund-etf.asp)\n

2. **Level 2 Instruments**
   - **Corporate Bonds**: Debt securities issued by corporations to raise capital. They offer higher yields but come with higher risk compared to government bonds.
     - [Investopedia: Corporate Bonds](https://www.investopedia.com/terms/c/corporate-bond.asp)\n
   - **Municipal Bonds**: Bonds issued by local governments or municipalities. Interest is often tax-exempt.
     - [Investopedia: Municipal Bonds](https://www.investopedia.com/terms/m/municipal-bond.asp)\n
   - **Interest Rate Swaps**: Contracts where parties exchange interest payments based on different interest rates.
     - [Investopedia: Interest Rate Swap](https://www.investopedia.com/terms/i/interestrateswap.asp)\n
   - **Currency Swaps**: Agreements to exchange principal and interest payments in different currencies.
     - [Investopedia: Currency Swap](https://www.investopedia.com/terms/c/currency-swap.asp)\n
   - **Credit Default Swaps (CDS)**: Contracts that provide protection against the default of a borrower.
     - [Investopedia: Credit Default Swap (CDS)](https://www.investopedia.com/terms/c/creditdefaultswap.asp)\n
   - **Money Market Instruments**
     - **Certificates of Deposit (CDs)**: Time deposits offered by banks with a fixed interest rate and maturity date.
       - [Investopedia: Certificate of Deposit (CD)](https://www.investopedia.com/terms/c/certificate-of-deposit.asp)\n
     - **Commercial Paper**: Short-term unsecured promissory notes issued by corporations to raise funds.
       - [Investopedia: Commercial Paper](https://www.investopedia.com/terms/c/commercialpaper.asp)\n
     - **Repurchase Agreements (Repos)**: Short-term borrowing where one party sells securities to another with an agreement to repurchase them at a later date.
       - [Investopedia: Repurchase Agreement (Repo)](https://www.investopedia.com/terms/r/repurchaseagreement.asp)\n
   - **Spot Contracts (Forex)**: Agreements to buy or sell a currency at the current exchange rate with immediate settlement.
     - [Investopedia: Spot Market](https://www.investopedia.com/terms/s/spotmarket.asp)\n
   - **Forward Contracts (Forex)**: Agreements to buy or sell a currency at a specified future date at an agreed-upon rate.
     - [Investopedia: Forward Contract](https://www.investopedia.com/terms/f/forwardcontract.asp)\n

3. **Level 3 Instruments**
   - **Exotic Options**
     - **Barrier Options**: Options that become active or void depending on whether the price of the underlying asset reaches a certain barrier level.
       - [Investopedia: Barrier Option](https://www.investopedia.com/terms/b/barrier-option.asp)\n
     - **Asian Options**: Options where the payoff is determined by the average price of the underlying asset over a certain period.
       - [Investopedia: Asian Option](https://www.investopedia.com/terms/a/asian-option.asp)\n
     - **Binary Options**: Options where the payoff is either a fixed amount or nothing at all, based on whether the underlying asset price is above or below a certain level.
       - [Investopedia: Binary Option](https://www.investopedia.com/terms/b/binaryoption.asp)\n
     - **Digital Options**: Similar to binary options, these offer a fixed payoff if a condition is met at expiration.
       - [Investopedia: Digital Option](https://www.investopedia.com/terms/d/digital-option.asp)\n
     - **Lookback Options**: Options where the payoff is based on the optimal price of the underlying asset over the life of the option.
       - [Investopedia: Lookback Option](https://www.investopedia.com/terms/l/lookback-option.asp)\n
     - **Chooser Options**: Options that give the holder the choice of whether to take a call or put option at a later date.
       - [Investopedia: Chooser Option](https://www.investopedia.com/terms/c/chooser-option.asp)\n
   - **Collateralized Debt Obligations (CDOs)**: Investment vehicles backed by a diversified pool of debt, including loans and bonds. The cash flows from the underlying assets are split into different tranches.
     - [Investopedia: Collateralized Debt Obligation (CDO)](https://www.investopedia.com/terms/c/cdo.asp)\n
   - **Credit-Linked Notes (CLNs)**: Debt instruments where payments are linked to the credit performance of a reference entity.
     - [Investopedia: Credit-Linked Note](https://www.investopedia.com/terms/c/credit-linked-note.asp)\n
   - **Mortgage-Backed Securities (MBS)**: Securities backed by a pool of mortgages. Investors receive payments derived from the underlying mortgage payments.
     - [Investopedia: Mortgage-Backed Securities](https://www.investopedia.com/terms/m/mortgage-backed-securities-mbs.asp)\n
   - **Structured Finance Products**
     - **Asset-Backed Securities (ABS)**: Financial securities backed by a pool of assets, such as loans or receivables.
       - [Investopedia: Asset-Backed Securities](https://www.investopedia.com/terms/a/asset-backed-securities-abs.asp)\n
     - **Collateralized Loan Obligations (CLOs)**: A type of CDO that is backed by a pool of loans, often corporate loans.
       - [Investopedia: Collateralized Loan Obligation (CLO)](https://www.investopedia.com/terms/c/collateralized-loan-obligation-clo.asp)\n
   - **Longevity Swaps**: Contracts where one party pays a fixed amount in exchange for payments based on the longevity of a population or individual.
     - [Investopedia: Longevity Swap](https://www.investopedia.com/terms/l/longevity-swap.asp)\n

4. **Specialty Instruments by Firm**
   - **Salomon Instruments**: Instruments used by Salomon Brothers, including certain types of mortgage-backed securities and structured finance products.
     - [Investopedia: Salomon Brothers](https://www.investopedia.com/terms/s/salomon-brothers.asp)\n
   - **Citi Instruments**: Instruments utilized by Citigroup, including particular types of callable equity-linked notes and complex derivatives.
     - [Investopedia: Citigroup](https://www.investopedia.com/terms/c/citigroup.asp)\n
   - **Lehman Instruments**: Instruments used by Lehman Brothers, including specific types of collateralized debt obligations (CDOs) and bespoke derivatives.
     - [Investopedia: Lehman Brothers](https://www.investopedia.com/terms/l/lehman-brothers.asp)\n
   - **Bear Stearns Instruments**: Instruments utilized by Bear Stearns, including particular types of CDOs and bespoke derivatives.
     - [Investopedia: Bear Stearns](https://www.investopedia.com/terms/b/bear-stearns.asp)\n"""
                break
            elif choice == 'q' or choice == 'quit':
                print("Quitting the program.")
                sys.exit()  # Exit the program
            else:
                print("Invalid choice. Please enter 1, 2, or Q.")

        return text_content

    # Clear the screen before starting the display
    os.system('clear' if os.name != 'nt' else 'cls')

    # Display hardcoded ASCII art
    display_hardcoded_ascii_art()

    # Prompt the user and get the choice
    text_content = prompt_user()

    # Display the selected text content normally
    display_text_normally(text_content)
def download_exchange_archives():
    os.makedirs(EXCHANGE_SOURCE_DIR, exist_ok=True)
    gamecat_ascii()

    def generate_urls():
        base_url = "https://www.sec.gov/files/opa/data/market-structure/metrics-individual-security-and-exchange/"
        # List of specific file names
        file_names = [
            "individual_security_exchange_2012_q1.zip",
            "individual_security_exchange_2012_q20.zip",
            "individual_security_exchange_2012_q30.zip",
            "individual_security_exchange_2012_q40.zip",
            "individual_security_exchange_2013_q10.zip",
            "individual_security_exchange_2013_q20.zip",
            "individual_security_exchange_2013_q30.zip",
            "individual_security_exchange_2013_q43.zip",
            "individual_security_exchange_2014_q1.zip",
            "individual_security_exchange_2014_q2.zip",
            "individual_security_exchange_2014_q3.zip",
            "individual_security_exchange_2014_q4.zip",
            "individual_security_exchange_2015_q1.zip",
            "individual_security_exchange_2015_q2.zip",
            "individual_security_exchange_2015_q3.zip",
            "individual_security_exchange_2015_q4.zip",
            "individual_security_exchange_2016_q1-v2.zip",
            "individual_security_exchange_2016_q2.zip",
            "individual_security_exchange_2016_q3.zip",
            "individual_security_exchange_2016_q4.zip",
            "individual_security_exchange_2017_q1.zip",
            "individual_security_exchange_2017_q2.zip",
            "individual_security_exchange_2017_q3.zip",
            "individual_security_exchange_2017_q4.zip",
            "individual_security_exchange_2018_q1.zip",
            "individual_security_exchange_2018_q2.zip",
            "individual_security_exchange_2018_q3.zip",
            "individual_security_exchange_2018_q4.zip",
            "individual_security_exchange_2019_q1.zip",
            "individual_security_exchange_2019_q2.zip",
            "individual_security_exchange_2019_q3.zip",
            "individual_security_exchange_2019_q4.zip",
            "individual_security_exchange_2020_q1.zip",
            "individual_security_exchange_2020_q2.zip",
            "individual_security_exchange_2020_q3.zip",
            "individual_security_exchange_2020_q4.zip",
            "individual_security_exchange_2021_q1.zip",
            "individual_security_exchange_2021_q2.zip",
            "individual_security_exchange_2021_q3.zip",
            "individual_security_exchange_2021_q4.zip",
            "individual_security_exchange_2022_q1.zip",
            "individual_security_exchange_2022_q2.zip",
            "individual_security_exchange_2022_q3.zip",
            "individual_security_exchange_2022_q4.zip",
            "individual_security_exchange_2023_q1.zip",
            "individual_security_exchange_2023_q2.zip",
            "individual_security_exchange_2023_q3.zip",
            "individual_security_exchange_2023_q4.zip",
            "individual_security_exchange_2024_q1.zip",
            "individual_security_exchange_2024_q2.zip",
            "individual_security_exchange_2024_q3.zip"
        ]

        def sort_key(filename):
            # Extract year and quarter, handle cases where the format might differ
            year_part = filename[31:35]
            quarter_part = filename[36:38]
            
            # Try to convert year to integer, if not possible, use 0 as a fallback
            try:
                year = int(year_part)
            except ValueError:
                year = 0  # or any other default value you see fit
                
            # Use the quarter as is, or modify if needed
            quarter = quarter_part
            
            return (year, quarter)

        sorted_file_names = sorted(file_names, key=sort_key)
        
        url_list = [f"{base_url}{file_name}" for file_name in sorted_file_names]
        return url_list

    urls = generate_urls()

    # Pass the generated URLs to download_archives
    download_archives(EXCHANGE_SOURCE_DIR, FILELIST, urls)

    print("Download of historical exchange volume archive completed.")
def download_insider_archives():
    os.makedirs(INSIDER_SOURCE_DIR, exist_ok=True)
    gamecat_ascii()

    def generate_urls():
        base_url = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/"
        # List of specific file names
        file_names = [
            "2006q1_form345.zip",
            "2006q2_form345.zip",
            "2006q3_form345.zip",
            "2006q4_form345.zip",
            "2007q1_form345.zip",
            "2007q2_form345.zip",
            "2007q3_form345.zip",
            "2007q4_form345.zip",
            "2008q1_form345.zip",
            "2008q2_form345.zip",
            "2008q3_form345.zip",
            "2008q4_form345.zip",
            "2009q1_form345.zip",
            "2009q2_form345.zip",
            "2009q3_form345.zip",
            "2009q4_form345.zip",
            "2010q1_form345.zip",
            "2010q2_form345.zip",
            "2010q3_form345.zip",
            "2010q4_form345.zip",
            "2011q1_form345.zip",
            "2011q2_form345.zip",
            "2011q3_form345.zip",
            "2011q4_form345.zip",
            "2012q1_form345.zip",
            "2012q2_form345.zip",
            "2012q3_form345.zip",
            "2012q4_form345.zip",
            "2013q1_form345.zip",
            "2013q2_form345.zip",
            "2013q3_form345.zip",
            "2013q4_form345.zip",
            "2014q1_form345.zip",
            "2014q2_form345.zip",
            "2014q3_form345.zip",
            "2014q4_form345.zip",
            "2015q1_form345.zip",
            "2015q2_form345.zip",
            "2015q3_form345.zip",
            "2015q4_form345.zip",
            "2016q1_form345.zip",
            "2016q2_form345.zip",
            "2016q3_form345.zip",
            "2016q4_form345.zip",
            "2017q1_form345.zip",
            "2017q2_form345.zip",
            "2017q3_form345.zip",
            "2017q4_form345.zip",
            "2018q1_form345.zip",
            "2018q2_form345.zip",
            "2018q3_form345.zip",
            "2018q4_form345.zip",
            "2019q1_form345.zip",
            "2019q2_form345.zip",
            "2019q3_form345.zip",
            "2019q4_form345.zip",
            "2020q1_form345.zip",
            "2020q2_form345.zip",
            "2020q3_form345.zip",
            "2020q4_form345.zip",
            "2021q1_form345.zip",
            "2021q2_form345.zip",
            "2021q3_form345.zip",
            "2021q4_form345.zip",
            "2022q1_form345.zip",
            "2022q2_form345.zip",
            "2022q3_form345.zip",
            "2022q4_form345.zip",
            "2023q1_form345.zip",
            "2023q2_form345.zip",
            "2023q3_form345.zip",
            "2023q4_form345.zip",
            "2024q1_form345.zip",
            "2024q2_form345.zip",
            "2024q3_form345.zip",
        ]
        def sort_key(filename):
            # Extract year and quarter, handle cases where the format might differ
            year_part = filename[31:35]
            quarter_part = filename[36:38]
            
            # Try to convert year to integer, if not possible, use 0 as a fallback
            try:
                year = int(year_part)
            except ValueError:
                year = 0  # or any other default value you see fit
                
            # Use the quarter as is, or modify if needed
            quarter = quarter_part
            
            return (year, quarter)

        sorted_file_names = sorted(file_names, key=sort_key)
        
        url_list = [f"{base_url}{file_name}" for file_name in sorted_file_names]
        return url_list

    urls = generate_urls()

    # Pass the generated URLs to download_archives
    download_archives(INSIDER_SOURCE_DIR, FILELIST, urls)

    print("Download of historical exchange volume archive completed.")
def allyourbasearebelongtous():
    file_queue = Queue()
    idx_file = os.path.join(EDGAR_SOURCE_DIR, "master.idx")
    log_file = os.path.join(EDGAR_SOURCE_DIR, "sec_download_log.txt")
    gamecat_ascii()
    
    # Configure logging to write to a file
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='error_log.txt',  
        filemode='w'  
    )

    # Log an error message
    logging.error("This is an error message")

    def log_progress(message):
        with open(log_file, 'a') as log:
            log.write(f"{datetime.now()}: {message}\n")
        print(message)

    def check_file_size(url):
        """Check the size of the file at the given URL."""
        try:
            headers = {'User-Agent': "anonymous/FORTHELULZ@anonyops.com"}
            response = requests.head(url, headers=headers, timeout=10)
            response.raise_for_status()
            return int(response.headers.get('Content-Length', 0))
        except requests.RequestException as e:
            print(f"Failed to get size for {url}: {e}")
            return None

    def download_file(url, download_directory):
        """Download a file from the given URL, log the download, and compute MD5 hash."""
        try:
            headers = {'User-Agent': "anonymous/FORTHELULZ@anonyops.com"}
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
        
            filename = url.split('/')[-1]
            cik = url.split('/data/')[1].split('/')[0]
            dir_path = os.path.join(download_directory, cik)
            os.makedirs(dir_path, exist_ok=True)
            filepath = os.path.join(dir_path, filename)
        
            if os.path.exists(filepath):
                with open(filepath, 'rb') as file:
                    file_hash = hashlib.md5()
                    while chunk := file.read(8192):
                        file_hash.update(chunk)
                    current_md5 = file_hash.hexdigest()
            
                log_file = os.path.join(download_directory, 'download_log.txt')
                if os.path.exists(log_file):
                    with open(log_file, 'r') as log:
                        for line in log:
                            parts = line.strip().split(',')
                            if len(parts) == 4 and parts[2] == filepath:
                                logged_md5 = parts[3]
                                if current_md5 == logged_md5:
                                    print(f"FILE already downloaded. {current_md5} verified: {filepath}")
                                    return True
    
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        
            with open(filepath, 'rb') as file:
                file_hash = hashlib.md5()
                while chunk := file.read(8192):
                    file_hash.update(chunk)
                md5_hash = file_hash.hexdigest()
        
            log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{url},{filepath},{md5_hash}\n"
            with open(log_file, 'a') as log:
                log.write(log_entry)
        
            print(f"Downloaded: {filepath}, MD5: {md5_hash}")
            return True
    
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return False
        
    def process_line(line):
        parts = line.split('|')
        if len(parts) >= 5:
            filename = parts[4].strip()
            if filename.endswith("Filename"):
                filename = filename.rsplit('/', 1)[0]
            url = f"https://www.sec.gov/Archives/{filename}"
            return url
        return None

    def extract_idx_from_zip(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith('.idx'):
                    idx_content = zip_ref.read(file_name).decode('utf-8', errors='ignore')
                    # Split by newline and skip the first 12 lines (assuming headers end at line 12)
                    return '\n'.join(idx_content.split('\n')[12:])
        raise FileNotFoundError("No IDX file found in ZIP archive.")

    def get_user_selection(zip_files):
        print("\nEnter a 4-digit year, 'qtr' for specific quarter, 'all' for all archives, or '0' to return to main menu:")
        while True:
            choice = input("Your choice: ").strip().lower()  # Convert to lowercase for consistency
            if choice == '0':
                return None
            elif choice == 'all':
                return zip_files  # Return all ZIP files
            elif choice == 'qtr':
                print("\nAvailable ZIP files:")
                for i, file in enumerate(zip_files, 1):
                    print(f"{i}. {file}")
                while True:
                    try:
                        choice = int(input("Enter the number of the ZIP file to process (or 0 to exit): "))
                        if choice == 0:
                            break
                        if 1 <= choice <= len(zip_files):
                            return [zip_files[choice - 1]]
                        print("Invalid choice. Please enter a number between 1 and", len(zip_files))
                    except ValueError:
                        print("Please enter a valid number.")
            elif choice.isdigit() and len(choice) == 4:
                year = choice
                print(f"Processing files for year {year}. Enter a quarter (1-4) or press Enter for all quarters:")
                quarter = input("Quarter (or press Enter for all): ").strip()
                if quarter and quarter.isdigit() and 1 <= int(quarter) <= 4:
                    year_files = [f for f in zip_files if f.startswith(year) and f.endswith(f"_QTR{quarter}.zip")]
                else:
                    year_files = [f for f in zip_files if f.startswith(year)]
            
                if year_files:
                    print(f"Processing files for year {year}, quarter {quarter if quarter else 'all'}:")
                    return year_files
                else:
                    print(f"No files found for year {year}, quarter {quarter if quarter else 'all'}.")
            else:
                print("Only 4-digit year, 'qtr', 'all', or '0' accepted. For example: 1999, qtr, all")

    def process_zip(zip_path):
        """Process a single ZIP file."""
        log_progress(f"Processing {zip_path}")
        idx_content = extract_idx_from_zip(zip_path)
        urls = [process_line(line) for line in idx_content.split('\n') if process_line(line)]
    
        downloaded = 0
        failed = 0
        total_files = len(urls)
    
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(download_file, url, EDGAR_SOURCE_DIR) for url in urls]
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    downloaded += 1
                else:
                    failed += 1
                log_progress(f"Downloaded {downloaded}/{total_files}, Failed {failed}")

        log_progress(f"Finished processing {zip_path}. Downloaded {downloaded}/{total_files}, Failed {failed}")

    def remove_top_lines(file_path, lines_to_remove=11):
        """Remove the top `lines_to_remove` lines from the given file."""
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        with open(file_path, 'w') as file:
            file.writelines(lines[lines_to_remove:])

    def compile_urls(zip_directory, idx_file):
        """Compile all URLs from the archives into master.idx."""
        print(f"Compiling URLs from {zip_directory} into {idx_file}.")
        for file in os.listdir(zip_directory):
            if file.endswith('.zip'):
                idx_file_path = extract_idx_from_zip(os.path.join(zip_directory, file))
                remove_top_lines(idx_file_path)
                with open(idx_file_path, 'r') as f:
                    content = f.read()
                with open(idx_file, 'a') as master_file:
                    master_file.write(content)
                os.remove(idx_file_path)
                print(f"Processed {file}")

    def scrape_sec(idx_file, download_directory):
        """Begin scraping the entire SEC."""
        os.makedirs(download_directory, exist_ok=True)
        print(f"Starting SEC scraping from {idx_file} to {download_directory}")

        with open(idx_file, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
        
        urls = [process_line(line) for line in lines if process_line(line) is not None]

        def download_file_task(url):
            return download_file(url, download_directory)
        
        failed_urls = []  # To track failed downloads

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(download_file_task, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url, success = future.result()
                if not success:
                    failed_urls.append(url)
                print(f"Downloaded {url} {'successfully' if success else 'with errors'}")

        print(f"Downloaded {len(urls) - len(failed_urls)} files successfully.")
        if failed_urls:
            print(f"Failed to download {len(failed_urls)} files.")

    try:
        # Ensure the master.idx file is empty or create it
        with open(idx_file, 'w') as master_file:
            master_file.write("")  # Clear the file if it exists

        zip_files = [f for f in os.listdir(EDGAR_SOURCE_DIR) if f.endswith('.zip')]

        while True:
            selected_zips = get_user_selection(zip_files)
            if not selected_zips and zip_files:  # Default to all ZIPs if none selected
                selected_zips = zip_files
            if not selected_zips:
                break
        
            total_files = sum(len([process_line(line) for line in extract_idx_from_zip(os.path.join(EDGAR_SOURCE_DIR, zip)).split('\n') if process_line(line)]) for zip in selected_zips)
        
            for zip_file in selected_zips:
                zip_path = os.path.join(EDGAR_SOURCE_DIR, zip_file)
                process_zip(zip_path)

        log_progress("SEC processing pipeline completed.")

    except Exception as e:
        log_progress(f"An error occurred: {e}")

    try:
        # Ensure the master.idx file is empty or create it
        with open(idx_file, 'w') as master_file:
            master_file.write("")  # Clear the file if it exists

        zip_files = [f for f in os.listdir(EDGAR_SOURCE_DIR) if f.endswith('.zip')]

        for zip_file in zip_files:
            zip_path = os.path.join(EDGAR_SOURCE_DIR, zip_file)
            try:
                print(f"Processing {zip_file}")
                idx_file_path = extract_idx_from_zip(zip_path)
                remove_top_lines(idx_file_path)
                
                with open(idx_file_path, 'r') as f:
                    content = f.read()
                file_queue.put(content)

                os.remove(idx_file_path)
                
                print(f"Successfully processed {zip_file}")
            except Exception as e:
                print(f"Error processing {zip_file}: {e}")

            # Write from the queue to the master.idx file after each zip file
            def write_to_master_file():
                while not file_queue.empty():
                    content = file_queue.get()
                    with open(idx_file, 'a') as master_file:
                        master_file.write(content)

            write_to_master_file()

        print("Compilation complete! uwu")

        # Verbose start of compile_urls and scrape_sec
        print("\nStarting to compile URLs from ZIP files...")
        start_time = time.time()
        compile_urls(EDGAR_SOURCE_DIR, idx_file)
        end_time = time.time()
        print(f"URL compilation completed in {end_time - start_time:.2f} seconds.")

        print("\nStarting to scrape SEC data...")
        start_time = time.time()
        scrape_sec(idx_file, EDGAR_SOURCE_DIR)
        end_time = time.time()
        print(f"SEC scraping completed in {end_time - start_time:.2f} seconds.")

    except Exception as e:
        print(f"An error occurred: {e}")
def download_credit_archives():
    os.makedirs(CREDIT_SOURCE_DIR, exist_ok=True)
    gamecat_ascii()

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/sec/SEC_CUMULATIVE_CREDITS_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    def download_zip_with_rate_limit(url):
        zip_filename = url.split('/')[-1]
        temp_zip_path = os.path.join(CREDIT_SOURCE_DIR, zip_filename)
        
        print(f"Attempting to download: {zip_filename}")
        
        if os.path.exists(temp_zip_path):
            logging.info(f"Skipping download of {zip_filename} as it already exists.")
            return

        try:
            req = requests.get(url, stream=True)
            req.raise_for_status()  # Raise an exception for bad status codes
            file_size = int(req.headers.get('Content-Length', 0))
            
            with open(temp_zip_path, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size_downloaded = os.path.getsize(temp_zip_path)
            download_time = datetime.now()
            
            logging.info(f"Downloaded: {url}")
            logging.info(f"Destination: {temp_zip_path}")
            logging.info(f"Timestamp: {download_time}")
            logging.info(f"Size: {file_size_downloaded} bytes")
            logging.info(f"Expected Size: {file_size} bytes")
            logging.info(f"File size match: {file_size == file_size_downloaded}")
            
            print(f"Successfully downloaded: {zip_filename}")
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)  # Sleep for 1 second
            
        except requests.RequestException as e:
            logging.error(f"Failed to download {url}: {e}")
            print(f"Failed to download: {zip_filename}")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)  # Approximately 2 years back, accounting for leap years
    urls = generate_urls(start_date, end_date)

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(download_zip_with_rate_limit, url) for url in urls]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in thread: {e}")

    print("Downloads completed.")
    # Display numbered prompt for archive type selection
    #print("Would you like to search? (y)es or (n)o?:")
    
    creditquery = input("Would you like to search? (y)es or (n)o?:").strip()
    if creditquery == 'y':
        credits_second()
    else:
        print("Y not pushed. exiting.")
        exit(1)
def credits_second():
    gamecat_ascii()

    def parse_zips_in_batches(batch_size=100):
        master = pd.DataFrame()  # Start with an empty dataframe
        zip_files = sorted(glob.glob(os.path.join(CREDIT_SOURCE_DIR, '*.zip')), key=lambda x: os.path.basename(x))
        total_files = len(zip_files)
        results_count = 0
        
        print(f"\nStarting to process {total_files} zip files...")
        for i in range(0, total_files, batch_size):
            batch = zip_files[i:i+batch_size]
            for index, zip_file in enumerate(batch, 1):
                print(f"\nProcessing file {i + index}/{total_files}: {zip_file}")
                try:
                    with ZipFile(zip_file, 'r') as zip_ref:
                        csv_filename = zip_ref.namelist()[0]  # Assuming only one CSV per zip
                        print(f"Reading CSV file: {csv_filename}")
                        with zip_ref.open(csv_filename) as csv_file:
                            df = pd.read_csv(csv_file, low_memory=False)
                            match_found = False
                            for column in df.columns:
                                if column in df.columns and df[column].astype(str).str.contains(search_term, case=False, na=False).any():
                                    print(f"Matches found in column: {column}")
                                    matching_rows = df[df[column].astype(str).str.contains(search_term, case=False, na=False)]
                                    master = pd.concat([master, matching_rows], ignore_index=True)
                                    results_count += len(matching_rows)
                                    match_found = True
                                    print(f"Added {len(matching_rows)} matching rows. Total matches so far: {results_count}")
                                    break  # We've found a match, no need to check other columns
                            if not match_found:
                                print(f"No matches found in {csv_filename}")         
                except Exception as e:
                    logging.error(f"Error processing {zip_file}: {e}")
                    print(f"Error occurred while processing {zip_file}. Continuing to next file.")
                print(f"Current matches count: {results_count}")
            
            # Optionally, save or perform operations on 'master' here if it's getting too large
        return master, results_count

    print("Press Enter when you are ready to parse the files, or type 'q' to quit.")
    user_input = input()
    if user_input.lower() != 'q':
        search_term = input("Enter the search term: ").strip()
        master, final_count = parse_zips_in_batches()
        master_csv_path = os.path.join(CREDIT_SOURCE_DIR, f"filtered_{search_term.replace(' ', '_')}.csv")
        master.to_csv(master_csv_path, index=False)
        print(f"\nSaving results to: {master_csv_path}")
        print(f"Total Matches Found: {final_count}")
        logging.info(f"Parsing completed. Master file saved as {master_csv_path}")
    else:
        print("Exiting script.")
def download_equities_archives():
    os.makedirs(EQUITY_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/sec/SEC_CUMULATIVE_EQUITIES_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    def download_zip(url):
        zip_filename = url.split('/')[-1]
        temp_zip_path = os.path.join(EQUITY_SOURCE_DIR, zip_filename)
        
        if os.path.exists(temp_zip_path):
            logging.info(f"Skipping download of {zip_filename} as it already exists.")
            return

        try:
            req = requests.get(url, stream=True)
            req.raise_for_status()  # Raise an exception for bad status codes
            file_size = int(req.headers.get('Content-Length', 0))
            
            with open(temp_zip_path, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size_downloaded = os.path.getsize(temp_zip_path)
            download_time = datetime.now()
            
            logging.info(f"Downloaded: {url}")
            logging.info(f"Destination: {temp_zip_path}")
            logging.info(f"Timestamp: {download_time}")
            logging.info(f"Size: {file_size_downloaded} bytes")
            logging.info(f"Expected Size: {file_size} bytes")
            logging.info(f"File size match: {file_size == file_size_downloaded}")
            
        except requests.RequestException as e:
            logging.error(f"Failed to download {url}: {e}")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)  # Approximately 2 years back, accounting for leap years
    urls = generate_urls(start_date, end_date)

    with ThreadPoolExecutor(max_workers=16) as executor:
        list(executor.map(download_zip, urls))  # Use list() to ensure all tasks are completed before moving on

    print("Downloads completed.")
    equitytquery = input("Would you like to search? (y)es or (n)o?:").strip()
    if equitytquery == 'y':
        equities_second()
    else:
        print("Y not pushed. exiting.")
        exit(1)
def equities_second():
    gamecat_ascii()
    
    def parse_zips(search_terms):
        master = pd.DataFrame()  # Start with an empty dataframe
        zip_files = sorted(glob.glob(os.path.join(EQUITY_SOURCE_DIR, '*.zip')), key=lambda x: os.path.basename(x))  # Sort by filename to keep dates in order
        first_file_processed = False
        first_headers = None
        total_files = len(zip_files)
        results_count = 0
        print(f"\nStarting to process {total_files} zip files...")
        for index, zip_file in enumerate(zip_files, 1):
            print(f"\nProcessing file {index}/{total_files}: {zip_file}")
            try:
                with ZipFile(zip_file, 'r') as zip_ref:
                    csv_filename = zip_ref.namelist()[0]  # Assuming only one CSV per zip
                    print(f"Reading CSV file: {csv_filename}")
                    with zip_ref.open(csv_filename) as csv_file:
                        df = pd.read_csv(csv_file, low_memory=False)
                        if not first_file_processed:
                            first_headers = df.columns.tolist()
                            first_file_processed = True
                        # Combine all columns into a single string per row
                        df['combined'] = df.apply(lambda row: ' '.join(row.astype(str)), axis=1)
                        # Create a pattern for OR condition
                        pattern = '|'.join(search_terms)
                        # Find rows where any search term appears
                        mask = df['combined'].str.contains(pattern, case=False, na=False)
                        matching_rows = df[mask]
                        # Drop the 'combined' column if it exists
                        if 'combined' in matching_rows.columns:
                            matching_rows = matching_rows.drop(columns=['combined'])
                        # Add to master
                        master = pd.concat([master, matching_rows], ignore_index=True)
                        results_count += len(matching_rows)
                        print(f"Added {len(matching_rows)} matching rows. Total matches so far: {results_count}")
            except Exception as e:
                logging.error(f"Error processing {zip_file}: {e}")
                print(f"Error occurred while processing {zip_file}. Continuing to next file.")
            print(f"Current matches count: {results_count}")
        
        # If we have processed at least one file, ensure the CSV starts with the first file's headers
        if first_headers:
            master = master.reindex(columns=first_headers, fill_value=None)
        return master, results_count

    print("Press Enter when you are ready to parse the files, or type 'q' to quit.")
    user_input = input()
    if user_input.lower() != 'q':
        search_terms_input = input("Enter search terms separated by commas: ").strip()
        search_terms = [term.strip() for term in search_terms_input.split(',')]
        if not search_terms:
            print("No search terms provided. Exiting.")
            return
        master, final_count = parse_zips(search_terms)
        safe_terms = [re.sub(r'\W+', '_', term) for term in search_terms]
        master_csv_path = os.path.join(EQUITY_SOURCE_DIR, f"filtered_{'_'.join(safe_terms)}.csv")
        master.to_csv(master_csv_path, index=False)
        print(f"\nSaving results to: {master_csv_path}")
        print(f"Total Matches Found: {final_count}")
        logging.info(f"Parsing completed. Master file saved as {master_csv_path}")
    else:
        print("Exiting script.")
def download_cftc_credit_archives():
    os.makedirs(CFTC_CREDIT_SOURCE_DIR, exist_ok=True)
    gamecat_ascii()
    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_CREDITS_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    def download_zip_with_rate_limit(url):
        zip_filename = url.split('/')[-1]
        temp_zip_path = os.path.join(CFTC_CREDIT_SOURCE_DIR, zip_filename)
        
        print(f"Attempting to download: {zip_filename}")
        
        if os.path.exists(temp_zip_path):
            logging.info(f"Skipping download of {zip_filename} as it already exists.")
            return

        try:
            req = requests.get(url, stream=True)
            req.raise_for_status()  # Raise an exception for bad status codes
            file_size = int(req.headers.get('Content-Length', 0))
            
            with open(temp_zip_path, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size_downloaded = os.path.getsize(temp_zip_path)
            download_time = datetime.now()
            
            logging.info(f"Downloaded: {url}")
            logging.info(f"Destination: {temp_zip_path}")
            logging.info(f"Timestamp: {download_time}")
            logging.info(f"Size: {file_size_downloaded} bytes")
            logging.info(f"Expected Size: {file_size} bytes")
            logging.info(f"File size match: {file_size == file_size_downloaded}")
            
            print(f"Successfully downloaded: {zip_filename}")
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)  # Sleep for 1 second
            
        except requests.RequestException as e:
            logging.error(f"Failed to download {url}: {e}")
            print(f"Failed to download: {zip_filename}")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)  # Approximately 2 years back, accounting for leap years
    urls = generate_urls(start_date, end_date)

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(download_zip_with_rate_limit, url) for url in urls]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in thread: {e}")

    print("Downloads completed.")
    # Display numbered prompt for archive type selection
    #print("Would you like to search? (y)es or (n)o?:")
    
    creditquery = input("Would you like to search? (y)es or (n)o?:").strip()
    if creditquery == 'y':
        CFTC_credits_second()
    else:
        print("Y not pushed. exiting.")
        exit(1)
def CFTC_credits_second():
    gamecat_ascii()

    def parse_zips_in_batches(batch_size=100):
        master = pd.DataFrame()  # Start with an empty dataframe
        zip_files = sorted(glob.glob(os.path.join(CFTC_CREDIT_SOURCE_DIR, '*.zip')), key=lambda x: os.path.basename(x))
        total_files = len(zip_files)
        results_count = 0
        
        print(f"\nStarting to process {total_files} zip files...")
        for i in range(0, total_files, batch_size):
            batch = zip_files[i:i+batch_size]
            for index, zip_file in enumerate(batch, 1):
                print(f"\nProcessing file {i + index}/{total_files}: {zip_file}")
                try:
                    with ZipFile(zip_file, 'r') as zip_ref:
                        csv_filename = zip_ref.namelist()[0]  # Assuming only one CSV per zip
                        print(f"Reading CSV file: {csv_filename}")
                        with zip_ref.open(csv_filename) as csv_file:
                            df = pd.read_csv(csv_file, low_memory=False)
                            match_found = False
                            for column in df.columns:
                                if column in df.columns and df[column].astype(str).str.contains(search_term, case=False, na=False).any():
                                    print(f"Matches found in column: {column}")
                                    matching_rows = df[df[column].astype(str).str.contains(search_term, case=False, na=False)]
                                    master = pd.concat([master, matching_rows], ignore_index=True)
                                    results_count += len(matching_rows)
                                    match_found = True
                                    print(f"Added {len(matching_rows)} matching rows. Total matches so far: {results_count}")
                                    break  # We've found a match, no need to check other columns
                            if not match_found:
                                print(f"No matches found in {csv_filename}")         
                except Exception as e:
                    logging.error(f"Error processing {zip_file}: {e}")
                    print(f"Error occurred while processing {zip_file}. Continuing to next file.")
                print(f"Current matches count: {results_count}")
            
            # Optionally, save or perform operations on 'master' here if it's getting too large
        return master, results_count

    print("Press Enter when you are ready to parse the files, or type 'q' to quit.")
    user_input = input()
    if user_input.lower() != 'q':
        search_term = input("Enter the search term: ").strip()
        master, final_count = parse_zips_in_batches()
        master_csv_path = os.path.join(CFTC_CREDIT_SOURCE_DIR, f"filtered_{search_term.replace(' ', '_')}.csv")
        master.to_csv(master_csv_path, index=False)
        print(f"\nSaving results to: {master_csv_path}")
        print(f"Total Matches Found: {final_count}")
        logging.info(f"Parsing completed. Master file saved as {master_csv_path}")
    else:
        print("Exiting script.")
def download_cftc_commodities_archives():
    os.makedirs(CFTC_COMMODITIES_SOURCE_DIR, exist_ok=True)
    gamecat_ascii()
    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_COMMODITIES_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list
    def download_zip_with_rate_limit(url):
        zip_filename = url.split('/')[-1]
        temp_zip_path = os.path.join(CFTC_COMMODITIES_SOURCE_DIR, zip_filename)
        
        print(f"Attempting to download: {zip_filename}")
        
        if os.path.exists(temp_zip_path):
            logging.info(f"Skipping download of {zip_filename} as it already exists.")
            return

        try:
            req = requests.get(url, stream=True)
            req.raise_for_status()  # Raise an exception for bad status codes
            file_size = int(req.headers.get('Content-Length', 0))
            
            with open(temp_zip_path, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size_downloaded = os.path.getsize(temp_zip_path)
            download_time = datetime.now()
            
            logging.info(f"Downloaded: {url}")
            logging.info(f"Destination: {temp_zip_path}")
            logging.info(f"Timestamp: {download_time}")
            logging.info(f"Size: {file_size_downloaded} bytes")
            logging.info(f"Expected Size: {file_size} bytes")
            logging.info(f"File size match: {file_size == file_size_downloaded}")
            
            print(f"Successfully downloaded: {zip_filename}")
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)  # Sleep for 1 second
            
        except requests.RequestException as e:
            logging.error(f"Failed to download {url}: {e}")
            print(f"Failed to download: {zip_filename}")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)  # Approximately 2 years back, accounting for leap years
    urls = generate_urls(start_date, end_date)

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(download_zip_with_rate_limit, url) for url in urls]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in thread: {e}")

    print("Downloads completed.")
    # Display numbered prompt for archive type selection
    #print("Would you like to search? (y)es or (n)o?:")
    
    creditquery = input("Would you like to search? (y)es or (n)o?:").strip()
    if creditquery == 'y':
        CFTC_commodities_second()
    else:
        print("Y not pushed. exiting.")
        exit(1)
def CFTC_commodities_second():
    gamecat_ascii()

    def parse_zips_in_batches(batch_size=100):
        master = pd.DataFrame()  # Start with an empty dataframe
        zip_files = sorted(glob.glob(os.path.join(CFTC_COMMODITIES_SOURCE_DIR, '*.zip')), key=lambda x: os.path.basename(x))
        total_files = len(zip_files)
        results_count = 0
        
        print(f"\nStarting to process {total_files} zip files...")
        for i in range(0, total_files, batch_size):
            batch = zip_files[i:i+batch_size]
            for index, zip_file in enumerate(batch, 1):
                print(f"\nProcessing file {i + index}/{total_files}: {zip_file}")
                try:
                    with ZipFile(zip_file, 'r') as zip_ref:
                        csv_filename = zip_ref.namelist()[0]  # Assuming only one CSV per zip
                        print(f"Reading CSV file: {csv_filename}")
                        with zip_ref.open(csv_filename) as csv_file:
                            df = pd.read_csv(csv_file, low_memory=False)
                            match_found = False
                            for column in df.columns:
                                if column in df.columns and df[column].astype(str).str.contains(search_term, case=False, na=False).any():
                                    print(f"Matches found in column: {column}")
                                    matching_rows = df[df[column].astype(str).str.contains(search_term, case=False, na=False)]
                                    master = pd.concat([master, matching_rows], ignore_index=True)
                                    results_count += len(matching_rows)
                                    match_found = True
                                    print(f"Added {len(matching_rows)} matching rows. Total matches so far: {results_count}")
                                    break  # We've found a match, no need to check other columns
                            if not match_found:
                                print(f"No matches found in {csv_filename}")         
                except Exception as e:
                    logging.error(f"Error processing {zip_file}: {e}")
                    print(f"Error occurred while processing {zip_file}. Continuing to next file.")
                print(f"Current matches count: {results_count}")
            
            # Optionally, save or perform operations on 'master' here if it's getting too large
        return master, results_count

    print("Press Enter when you are ready to parse the files, or type 'q' to quit.")
    user_input = input()
    if user_input.lower() != 'q':
        search_term = input("Enter the search term: ").strip()
        master, final_count = parse_zips_in_batches()
        master_csv_path = os.path.join(CFTC_CREDIT_SOURCE_DIR, f"filtered_{search_term.replace(' ', '_')}.csv")
        master.to_csv(master_csv_path, index=False)
        print(f"\nSaving results to: {master_csv_path}")
        print(f"Total Matches Found: {final_count}")
        logging.info(f"Parsing completed. Master file saved as {master_csv_path}")
    else:
        print("Exiting script.")
def download_cftc_rates_archives():
    os.makedirs(CFTC_RATES_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    def download_zip(url):
        zip_filename = url.split('/')[-1]
        temp_zip_path = os.path.join(CFTC_RATES_SOURCE_DIR, zip_filename)
        
        if os.path.exists(temp_zip_path):
            logging.info(f"Skipping download of {zip_filename} as it already exists.")
            return

        try:
            req = requests.get(url, stream=True)
            req.raise_for_status()  # Raise an exception for bad status codes
            file_size = int(req.headers.get('Content-Length', 0))
            
            with open(temp_zip_path, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size_downloaded = os.path.getsize(temp_zip_path)
            download_time = datetime.now()
            
            logging.info(f"Downloaded: {url}")
            logging.info(f"Destination: {temp_zip_path}")
            logging.info(f"Timestamp: {download_time}")
            logging.info(f"Size: {file_size_downloaded} bytes")
            logging.info(f"Expected Size: {file_size} bytes")
            logging.info(f"File size match: {file_size == file_size_downloaded}")
            
        except requests.RequestException as e:
            logging.error(f"Failed to download {url}: {e}")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)  # Approximately 2 years back, accounting for leap years
    urls = generate_urls(start_date, end_date)

    with ThreadPoolExecutor(max_workers=16) as executor:
        list(executor.map(download_zip, urls))  # Use list() to ensure all tasks are completed before moving on

    print("Downloads completed.")
    equitytquery = input("Would you like to search? (y)es or (n)o?:").strip()
    if equitytquery == 'y':
        cftc_rates_second()
    else:
        print("Y not pushed. exiting.")
        exit(1)
def cftc_rates_second():
    gamecat_ascii()

    def process_zip(zip_file):
        results = []
        try:
            with ZipFile(zip_file, 'r') as zip_ref:
                csv_filename = zip_ref.namelist()[0]  # Assuming only one CSV per zip
                with zip_ref.open(csv_filename) as csv_file:
                    df = pd.read_csv(csv_file, low_memory=False)
                    for column in df.columns:
                        if column in df.columns and df[column].astype(str).str.contains(search_term, case=False, na=False).any():
                            matching_rows = df[df[column].astype(str).str.contains(search_term, case=False, na=False)]
                            results.extend(matching_rows.to_dict('records'))  # Convert matching rows to list of dicts
                            break  # We've found a match, no need to check other columns
        except Exception as e:
            logging.error(f"Error processing {zip_file}: {e}")
        return results

    def write_to_csv(results, csv_writer):
        for row in results:
            csv_writer.writerow(row)

    # Main execution
    print("Press Enter when you are ready to parse the files, or type 'q' to quit.")
    user_input = input()
    if user_input.lower() != 'q':
        search_term = input("Enter the search term: ").strip()
        zip_files = sorted(glob.glob(os.path.join(CFTC_RATES_SOURCE_DIR, '*.zip')), key=lambda x: os.path.basename(x))
        total_files = len(zip_files)
        print(f"\nStarting to process {total_files} zip files with 7 worker threads...")

        master_csv_path = os.path.join(CFTC_RATES_SOURCE_DIR, f"filtered_{search_term.replace(' ', '_')}.csv")
        
        with open(master_csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=None)  # We'll define fieldnames later
            header_written = False

            with ThreadPoolExecutor(max_workers=7) as executor:
                # Process zip files
                future_to_zip = {executor.submit(process_zip, zip_file): zip_file for zip_file in zip_files}
                
                for future in as_completed(future_to_zip):
                    zip_file = future_to_zip[future]
                    try:
                        results = future.result()
                        if results and not header_written:
                            # Write header only once
                            csv_writer.fieldnames = results[0].keys()
                            csv_writer.writeheader()
                            header_written = True
                        write_to_csv(results, csv_writer)
                        print(f"Processed: {zip_file}")
                    except Exception as e:
                        print(f"Exception in {zip_file}: {e}")
            
            print(f"\nSaving results to: {master_csv_path}")
        logging.info(f"Parsing completed. Master file saved as {master_csv_path}")
    else:
        print("Exiting script.")
def download_cftc_equities_archives():
    os.makedirs(CFTC_EQUITY_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_EQUITIES_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    def download_zip(url):
        zip_filename = url.split('/')[-1]
        temp_zip_path = os.path.join(CFTC_EQUITY_SOURCE_DIR, zip_filename)
        
        if os.path.exists(temp_zip_path):
            logging.info(f"Skipping download of {zip_filename} as it already exists.")
            return

        try:
            req = requests.get(url, stream=True)
            req.raise_for_status()  # Raise an exception for bad status codes
            file_size = int(req.headers.get('Content-Length', 0))
            
            with open(temp_zip_path, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size_downloaded = os.path.getsize(temp_zip_path)
            download_time = datetime.now()
            
            logging.info(f"Downloaded: {url}")
            logging.info(f"Destination: {temp_zip_path}")
            logging.info(f"Timestamp: {download_time}")
            logging.info(f"Size: {file_size_downloaded} bytes")
            logging.info(f"Expected Size: {file_size} bytes")
            logging.info(f"File size match: {file_size == file_size_downloaded}")
            
        except requests.RequestException as e:
            logging.error(f"Failed to download {url}: {e}")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)  # Approximately 2 years back, accounting for leap years
    urls = generate_urls(start_date, end_date)

    with ThreadPoolExecutor(max_workers=16) as executor:
        list(executor.map(download_zip, urls))  # Use list() to ensure all tasks are completed before moving on

    print("Downloads completed.")
    equitytquery = input("Would you like to search? (y)es or (n)o?:").strip()
    if equitytquery == 'y':
        cftc_equities_second()
    else:
        print("Y not pushed. exiting.")
        exit(1)
def cftc_equities_second():
    gamecat_ascii()

    def process_zip(zip_file):
        results = []
        try:
            with ZipFile(zip_file, 'r') as zip_ref:
                csv_filename = zip_ref.namelist()[0]  # Assuming only one CSV per zip
                with zip_ref.open(csv_filename) as csv_file:
                    df = pd.read_csv(csv_file, low_memory=False)
                    for column in df.columns:
                        if column in df.columns and df[column].astype(str).str.contains(search_term, case=False, na=False).any():
                            matching_rows = df[df[column].astype(str).str.contains(search_term, case=False, na=False)]
                            results.extend(matching_rows.to_dict('records'))  # Convert matching rows to list of dicts
                            break  # We've found a match, no need to check other columns
        except Exception as e:
            logging.error(f"Error processing {zip_file}: {e}")
        return results

    def write_to_csv(results, csv_writer):
        for row in results:
            csv_writer.writerow(row)

    # Main execution
    print("Press Enter when you are ready to parse the files, or type 'q' to quit.")
    user_input = input()
    if user_input.lower() != 'q':
        search_term = input("Enter the search term: ").strip()
        zip_files = sorted(glob.glob(os.path.join(CFTC_EQUITY_SOURCE_DIR, '*.zip')), key=lambda x: os.path.basename(x))
        total_files = len(zip_files)
        print(f"\nStarting to process {total_files} zip files with 7 worker threads...")

        master_csv_path = os.path.join(CFTC_EQUITY_SOURCE_DIR, f"filtered_{search_term.replace(' ', '_')}.csv")
        
        with open(master_csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=None)  # We'll define fieldnames later
            header_written = False

            with ThreadPoolExecutor(max_workers=7) as executor:
                # Process zip files
                future_to_zip = {executor.submit(process_zip, zip_file): zip_file for zip_file in zip_files}
                
                for future in as_completed(future_to_zip):
                    zip_file = future_to_zip[future]
                    try:
                        results = future.result()
                        if results and not header_written:
                            # Write header only once
                            csv_writer.fieldnames = results[0].keys()
                            csv_writer.writeheader()
                            header_written = True
                        write_to_csv(results, csv_writer)
                        print(f"Processed: {zip_file}")
                    except Exception as e:
                        print(f"Exception in {zip_file}: {e}")
            
            print(f"\nSaving results to: {master_csv_path}")
        logging.info(f"Parsing completed. Master file saved as {master_csv_path}")
    else:
        print("Exiting script.")
def download_cftc_forex_archives():
    os.makedirs(CFTC_FOREX_SOURCE_DIR, exist_ok=True)

    def generate_urls(start_date, end_date):
        url_list = []
        current_date = start_date
        base_url = "https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_FOREX_"
        while current_date <= end_date:
            date_str = current_date.strftime('%Y_%m_%d')
            url_list.append(f"{base_url}{date_str}.zip")
            current_date += timedelta(days=1)
        return url_list

    def download_zip(url):
        zip_filename = url.split('/')[-1]
        temp_zip_path = os.path.join(CFTC_FOREX_SOURCE_DIR, zip_filename)
        
        if os.path.exists(temp_zip_path):
            logging.info(f"Skipping download of {zip_filename} as it already exists.")
            return

        try:
            req = requests.get(url, stream=True)
            req.raise_for_status()  # Raise an exception for bad status codes
            file_size = int(req.headers.get('Content-Length', 0))
            
            with open(temp_zip_path, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size_downloaded = os.path.getsize(temp_zip_path)
            download_time = datetime.now()
            
            logging.info(f"Downloaded: {url}")
            logging.info(f"Destination: {temp_zip_path}")
            logging.info(f"Timestamp: {download_time}")
            logging.info(f"Size: {file_size_downloaded} bytes")
            logging.info(f"Expected Size: {file_size} bytes")
            logging.info(f"File size match: {file_size == file_size_downloaded}")
            
        except requests.RequestException as e:
            logging.error(f"Failed to download {url}: {e}")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=2*365)  # Approximately 2 years back, accounting for leap years
    urls = generate_urls(start_date, end_date)

    with ThreadPoolExecutor(max_workers=16) as executor:
        list(executor.map(download_zip, urls))  # Use list() to ensure all tasks are completed before moving on

    print("Downloads completed.")
    equitytquery = input("Would you like to search? (y)es or (n)o?:").strip()
    if equitytquery == 'y':
        cftc_forex_second()
    else:
        print("Y not pushed. exiting.")
        exit(1)
def cftc_forex_second():
    gamecat_ascii()

    def process_zip(zip_file):
        results = []
        try:
            with ZipFile(zip_file, 'r') as zip_ref:
                csv_filename = zip_ref.namelist()[0]  # Assuming only one CSV per zip
                with zip_ref.open(csv_filename) as csv_file:
                    df = pd.read_csv(csv_file, low_memory=False)
                    for column in df.columns:
                        if column in df.columns and df[column].astype(str).str.contains(search_term, case=False, na=False).any():
                            matching_rows = df[df[column].astype(str).str.contains(search_term, case=False, na=False)]
                            results.extend(matching_rows.to_dict('records'))  # Convert matching rows to list of dicts
                            break  # We've found a match, no need to check other columns
        except Exception as e:
            logging.error(f"Error processing {zip_file}: {e}")
        return results

    def write_to_csv(results, csv_writer):
        for row in results:
            csv_writer.writerow(row)

    # Main execution
    print("Press Enter when you are ready to parse the files, or type 'q' to quit.")
    user_input = input()
    if user_input.lower() != 'q':
        search_term = input("Enter the search term: ").strip()
        zip_files = sorted(glob.glob(os.path.join(CFTC_FOREX_SOURCE_DIR, '*.zip')), key=lambda x: os.path.basename(x))
        total_files = len(zip_files)
        print(f"\nStarting to process {total_files} zip files with 7 worker threads...")

        master_csv_path = os.path.join(CFTC_FOREX_SOURCE_DIR, f"filtered_{search_term.replace(' ', '_')}.csv")
        
        with open(master_csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=None)  # We'll define fieldnames later
            header_written = False

            with ThreadPoolExecutor(max_workers=7) as executor:
                # Process zip files
                future_to_zip = {executor.submit(process_zip, zip_file): zip_file for zip_file in zip_files}
                
                for future in as_completed(future_to_zip):
                    zip_file = future_to_zip[future]
                    try:
                        results = future.result()
                        if results and not header_written:
                            # Write header only once
                            csv_writer.fieldnames = results[0].keys()
                            csv_writer.writeheader()
                            header_written = True
                        write_to_csv(results, csv_writer)
                        print(f"Processed: {zip_file}")
                    except Exception as e:
                        print(f"Exception in {zip_file}: {e}")
            
            print(f"\nSaving results to: {master_csv_path}")
        logging.info(f"Parsing completed. Master file saved as {master_csv_path}")
    else:
        print("Exiting script.")
def download_ncen_archives():
    BASE_URL = "https://www.sec.gov/files/dera/data/form-n-cen-data-sets/"
    urls = [
        BASE_URL + "2019q3_ncen.zip",
        BASE_URL + "2019q4_ncen.zip",
        BASE_URL + "2020q1_ncen.zip",
        BASE_URL + "2020q2_ncen.zip",
        BASE_URL + "2020q3_ncen.zip",
        BASE_URL + "2020q4_ncen.zip",
        BASE_URL + "2021q1_ncen.zip",
        BASE_URL + "2021q2_ncen.zip",
        BASE_URL + "2021q3_ncen.zip",
        BASE_URL + "2021q4_ncen.zip",
        BASE_URL + "2022q1_ncen.zip",
        BASE_URL + "2022q2_ncen.zip",
        BASE_URL + "2022q3_ncen.zip",
        BASE_URL + "2022q4_ncen.zip",
        BASE_URL + "2023q1_ncen.zip",
        BASE_URL + "2023q2_ncen.zip",
        BASE_URL + "2023q3_ncen.zip",
        BASE_URL + "2023q4_ncen.zip",
        BASE_URL + "2024q1_ncen.zip",
        BASE_URL + "2024q2_ncen.zip",
        BASE_URL + "2024q3_ncen.zip",
        BASE_URL + "2024q4_ncen.zip",
        BASE_URL + "2025q1_ncen.zip",
        BASE_URL + "2025q2_ncen.zip",
    ]
    
    download_archives(NCEN_SOURCE_DIR, FILELIST, urls)
def download_nport_archives():
    BASE_URL = "https://www.sec.gov/files/dera/data/form-n-port-data-sets/"
    urls = [
        BASE_URL + "2019q4_nport.zip",
        BASE_URL + "2020q1_nport.zip",
        BASE_URL + "2020q2_nport.zip",
        BASE_URL + "2020q3_nport.zip",
        BASE_URL + "2020q4_nport.zip",
        BASE_URL + "2021q1_nport.zip",
        BASE_URL + "2021q2_nport.zip",
        BASE_URL + "2021q3_nport.zip",
        BASE_URL + "2021q4_nport.zip",
        BASE_URL + "2022q1_nport.zip",
        BASE_URL + "2022q2_nport.zip",
        BASE_URL + "2022q3_nport.zip",
        BASE_URL + "2022q4_nport.zip",
        BASE_URL + "2023q1_nport.zip",
        BASE_URL + "2023q2_nport.zip",
        BASE_URL + "2023q3_nport.zip",
        BASE_URL + "2023q4_nport.zip",
        BASE_URL + "2024q1_nport.zip",
        BASE_URL + "2024q2_nport.zip",
        BASE_URL + "2024q3_nport.zip",
        BASE_URL + "2024q4_nport.zip",
        BASE_URL + "2025q1_nport.zip",
        BASE_URL + "2025q2_nport.zip",
    ]
    
    download_archives(NPORT_SOURCE_DIR, FILELIST, urls)
def download_13F_archives():
    BASE_URL = "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/"
    urls = [
        BASE_URL + "2013q2_form13f.zip",
        BASE_URL + "2013q3_form13f.zip",
        BASE_URL + "2013q4_form13f.zip",
        BASE_URL + "2014q1_form13f.zip",
        BASE_URL + "2014q2_form13f.zip",
        BASE_URL + "2014q3_form13f.zip",
        BASE_URL + "2014q4_form13f.zip",
        BASE_URL + "2015q1_form13f.zip",
        BASE_URL + "2015q2_form13f.zip",
        BASE_URL + "2015q3_form13f.zip",
        BASE_URL + "2015q4_form13f.zip",
        BASE_URL + "2016q1_form13f.zip",
        BASE_URL + "2016q2_form13f.zip",
        BASE_URL + "2016q3_form13f.zip",
        BASE_URL + "2016q4_form13f.zip",
        BASE_URL + "2017q1_form13f.zip",
        BASE_URL + "2017q2_form13f.zip",
        BASE_URL + "2017q3_form13f.zip",
        BASE_URL + "2017q4_form13f.zip",
        BASE_URL + "2018q1_form13f.zip",
        BASE_URL + "2018q2_form13f.zip",
        BASE_URL + "2018q3_form13f.zip",
        BASE_URL + "2018q4_form13f.zip",
        BASE_URL + "2019q1_form13f.zip",
        BASE_URL + "2019q2_form13f.zip",
        BASE_URL + "2019q3_form13f.zip",
        BASE_URL + "2019q4_form13f.zip",
        BASE_URL + "2020q1_form13f.zip",
        BASE_URL + "2020q2_form13f.zip",
        BASE_URL + "2020q3_form13f.zip",
        BASE_URL + "2020q4_form13f.zip",
        BASE_URL + "2021q1_form13f.zip",
        BASE_URL + "2021q2_form13f.zip",
        BASE_URL + "2021q3_form13f.zip",
        BASE_URL + "2021q4_form13f.zip",
        BASE_URL + "2022q1_form13f.zip",
        BASE_URL + "2022q2_form13f.zip",
        BASE_URL + "2022q3_form13f.zip",
        BASE_URL + "2022q4_form13f.zip",
        BASE_URL + "2023q1_form13f.zip",
        BASE_URL + "2023q2_form13f.zip",
        BASE_URL + "2023q3_form13f.zip",
        BASE_URL + "2023q4_form13f.zip",
        BASE_URL + "01jan2024-29feb2024_form13f.zip",
        BASE_URL + "01mar2024-31may2024_form13f.zip",
        BASE_URL + "01jun2024-31aug2024_form13f.zip",
        BASE_URL + "01sep2024-30nov2024_form13f.zip",
    ]
    
    download_archives(THRTNF_SOURCE_DIR, FILELIST, urls)
def download_nmfp_archives():
    BASE_URL = "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/"
    urls = [
        BASE_URL + "2010q4_nmfp.zip",
        BASE_URL + "2011q1_nmfp.zip",
        BASE_URL + "2011q2_nmfp.zip",
        BASE_URL + "2011q3_nmfp.zip",
        BASE_URL + "2011q4_nmfp.zip",
        BASE_URL + "2012q1_nmfp.zip",
        BASE_URL + "2012q2_nmfp.zip",
        BASE_URL + "2012q3_nmfp.zip",
        BASE_URL + "2012q4_nmfp.zip",
        BASE_URL + "2013q1_nmfp.zip",
        BASE_URL + "2013q2_nmfp.zip",
        BASE_URL + "2013q3_nmfp.zip",
        BASE_URL + "2013q4_nmfp.zip",
        BASE_URL + "2014q1_nmfp.zip",
        BASE_URL + "2014q2_nmfp.zip",
        BASE_URL + "2014q3_nmfp.zip",
        BASE_URL + "2014q4_nmfp.zip",
        BASE_URL + "2015q1_nmfp.zip",
        BASE_URL + "2015q2_nmfp.zip",
        BASE_URL + "2015q3_nmfp.zip",
        BASE_URL + "2015q4_nmfp.zip",
        BASE_URL + "2016q1_nmfp.zip",
        BASE_URL + "2016q2_nmfp.zip",
        BASE_URL + "2016q3_nmfp.zip",
        BASE_URL + "2016q4_nmfp.zip",
        BASE_URL + "2017q1_nmfp.zip",
        BASE_URL + "2017q2_nmfp.zip",
        BASE_URL + "2017q3_nmfp.zip",
        BASE_URL + "2017q4_nmfp.zip",
        BASE_URL + "2018q1_nmfp.zip",
        BASE_URL + "2018q2_nmfp.zip",
        BASE_URL + "2018q3_nmfp.zip",
        BASE_URL + "2018q4_nmfp.zip",
        BASE_URL + "2019q1_nmfp.zip",
        BASE_URL + "2019q2_nmfp.zip",
        BASE_URL + "2019q3_nmfp.zip",
        BASE_URL + "2019q4_nmfp.zip",
        BASE_URL + "2020q1_nmfp.zip",
        BASE_URL + "2020q2_nmfp.zip",
        BASE_URL + "2020q3_nmfp.zip",
        BASE_URL + "2020q4_nmfp.zip",
        BASE_URL + "2021q1_nmfp.zip",
        BASE_URL + "2021q2_nmfp.zip",
        BASE_URL + "2021q3_nmfp.zip",
        BASE_URL + "2021q4_nmfp.zip",
        BASE_URL + "2022q1_nmfp.zip",
        BASE_URL + "2022q2_nmfp.zip",
        BASE_URL + "20221007_nmfp.zip",
        BASE_URL + "20220701-20220710_nmfp",
        BASE_URL + "20220808-20220908_nmfp.zip",
        BASE_URL + "20221108-20221207_nmfp.zip",
        BASE_URL + "20221208-20230109_nmfp.zip",
        BASE_URL + "20230110-20230207_nmfp.zip",
        BASE_URL + "20230208-20230307_nmfp.zip",
        BASE_URL + "20230308-20230410_nmfp.zip",
        BASE_URL + "20230411-20230505_nmfp.zip",
        BASE_URL + "20230508-20230607_nmfp.zip",
        BASE_URL + "20230608-20230711_nmfp.zip",
        BASE_URL + "20230712-20230807_nmfp.zip",
        BASE_URL + "20230808-20230911_nmfp.zip",
        BASE_URL + "20230912-20231006_nmfp.zip",
        BASE_URL + "20231010-20231107_nmfp.zip",
        BASE_URL + "20231108-20231207_nmfp.zip",
        BASE_URL + "20231208-20240108_nmfp.zip",
        BASE_URL + "20240109-20240207_nmfp.zip",
        BASE_URL + "20240208-20240307_nmfp.zip",
        BASE_URL + "20240308-20240405_nmfp.zip",
        BASE_URL + "20240408-20240507_nmfp.zip",
        BASE_URL + "20240508-20240607_nmfp.zip",
    ]
    
    download_archives(NMFP_SOURCE_DIR, FILELIST, urls)
def download_formd_archives():
    BASE_URL = "https://www.sec.gov/files/structureddata/data/form-d-data-sets/"
    urls = [
        BASE_URL + "2008q1_d.zip",
        BASE_URL + "2008q2_d_0.zip",
        BASE_URL + "2008q3_d_0.zip",
        BASE_URL + "2008q4_d_0.zip",
        BASE_URL + "2009q1_d_0.zip",
        BASE_URL + "2009q2_d_0.zip",
        BASE_URL + "2009q3_d_0.zip",
        BASE_URL + "2009q4_d_0.zip",
        BASE_URL + "2010q1_d_0.zip",
        BASE_URL + "2010q2_d_0.zip",
        BASE_URL + "2010q3_d_0.zip",
        BASE_URL + "2010q4_d_0.zip",
        BASE_URL + "2011q1_d_0.zip",
        BASE_URL + "2011q2_d_0.zip",
        BASE_URL + "2011q3_d_0.zip",
        BASE_URL + "2011q4_d_0.zip",
        BASE_URL + "2012q1_d.zip",
        BASE_URL + "2012q2_d_0.zip",
        BASE_URL + "2012q3_d_0.zip",
        BASE_URL + "2012q4_d_0.zip",
        BASE_URL + "2013q1_d_0.zip",
        BASE_URL + "2013q2_d_0.zip",
        BASE_URL + "2013q3_d_0.zip",
        BASE_URL + "2013q4_d_0.zip",
        BASE_URL + "2014q1_d.zip",
        BASE_URL + "2014q2_d.zip",
        BASE_URL + "2014q3_d.zip",
        BASE_URL + "2014q4_d.zip",
        BASE_URL + "2015q1_d.zip",
        BASE_URL + "2015q2_d.zip",
        BASE_URL + "2015q3_d.zip",
        BASE_URL + "2015q4_d.zip",
        BASE_URL + "2016q1_d.zip",
        BASE_URL + "2016q2_d.zip",
        BASE_URL + "2016q3_d.zip",
        BASE_URL + "2016q4_d.zip",
        BASE_URL + "2017q1_d.zip",
        BASE_URL + "2017q2_d.zip",
        BASE_URL + "2017q3_d.zip",
        BASE_URL + "2017q4_d.zip",
        BASE_URL + "2018q1_d.zip",
        BASE_URL + "2018q2_d.zip",
        BASE_URL + "2018q3_d.zip",
        BASE_URL + "2018q4_d.zip",
        BASE_URL + "2019q1_d.zip",
        BASE_URL + "2019q2_d.zip",
        BASE_URL + "2019q3_d.zip",
        BASE_URL + "2019q4_d.zip",
        BASE_URL + "2020q1_d.zip",
        BASE_URL + "2020q2_d.zip",
        BASE_URL + "2020q3_d.zip",
        BASE_URL + "2020q4_d.zip",
        BASE_URL + "2021q1_d.zip",
        BASE_URL + "2021q2_d.zip",
        BASE_URL + "2021q3_d.zip",
        BASE_URL + "2021q4_d.zip",
        BASE_URL + "2022q1_d.zip",
        BASE_URL + "2022q2_d.zip",
        BASE_URL + "2022q3_d.zip",
        BASE_URL + "2022q4_d.zip",
        BASE_URL + "2023q1_d.zip",
        BASE_URL + "2023q2_d.zip",
        BASE_URL + "2023q3_d.zip",
        BASE_URL + "2023q4_d.zip",
        BASE_URL + "2024q1_d.zip",
        BASE_URL + "2024q2_d.zip",
        BASE_URL + "2024q3_d.zip",
    ]
    
    download_archives(FORMD_SOURCE_DIR, FILELIST, urls)
def download_edgar_archives():
    global failed_downloads
    global verbose
    global edgar_url
    global headers
    global backup_headers
    global files_found_count
    global done
    global base_path
    gamecat_ascii()

    # Create a list of all subdirectories from 1993 to 2024, including all four quarters
    years = range(1993, 2025)
    quarters = ["QTR1", "QTR2", "QTR3", "QTR4"]
    base_url = "https://www.sec.gov/Archives/edgar/full-index"

    subdirectories = [
        f"{base_url}/{year}/{quarter}/master.zip"
        for year in years
        for quarter in quarters
        if not (year == 2024 and quarter in ["QTR3", "QTR4"])
    ]
    failed_downloads = []
    processes = []
    additional_urls = [
        "https://raw.githubusercontent.com/ngshya/pfsm/master/data/sec_edgar_company_info.csv",
        "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
    ]
    
    def check_free_space():
        total_size = sum(os.path.getsize(os.path.join(EDGAR_SOURCE_DIR, f)) for f in os.listdir(EDGAR_SOURCE_DIR) if f.endswith('.zip'))
        free_space = shutil.disk_usage(EDGAR_SOURCE_DIR).free
        print(f"Total size needed: {total_size} bytes, Free space available: {free_space} bytes")
        return free_space > total_size

    def download_edgar_files():
        # Download master index files
        for url in tqdm(subdirectories, desc="Downloading EDGAR Master Index", unit="file"):
            year, quarter = url.split('/')[-3:-1]
            filename = f"{year}_{quarter}.zip"
            output_path = os.path.join(EDGAR_SOURCE_DIR, filename)
            
            if os.path.exists(output_path):
                continue  # Skip if already exists

            for attempt in range(3):
                try:
                    headers = {'User-Agent': "anonymous/FORTHELULZ@anonyops.com"}
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as response:
                        with open(output_path, 'wb') as file:
                            file.write(response.read())
                    print(f"Downloaded {url} to {output_path}")
                    break
                except (urllib.error.HTTPError, urllib.error.URLError) as e:
                    print(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt < 2:
                        time.sleep(1)  # Small delay before retry
            else:
                print(f"Failed to download {url} after 3 attempts")
                failed_downloads.append(url)

        # Download additional static files
        for url in tqdm(additional_urls, desc="Downloading Additional Files", unit="file"):
            filename = url.split('/')[-1]
            output_path = os.path.join(EDGAR_SOURCE_DIR, filename)
            
            if os.path.exists(output_path):
                continue  # Skip if already exists

            for attempt in range(3):
                try:
                    headers = {'User-Agent': "anonymous/FORTHELULZ@anonyops.com"}
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as response:
                        with open(output_path, 'wb') as file:
                            file.write(response.read())
                    print(f"Downloaded {url} to {output_path}")
                    break
                except (urllib.error.HTTPError, urllib.error.URLError) as e:
                    print(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt < 2:
                        time.sleep(1)  # Small delay before retry
            else:
                print(f"Failed to download {url} after 3 attempts")
                failed_downloads.append(url)

        # Daily index files download logic
        daily_base_url = "https://www.sec.gov/Archives/edgar/daily-index/"
        today = datetime.now()
        end_date = today - timedelta(days=1)
        daily_index_log = os.path.join(EDGAR_SOURCE_DIR, "daily-index-log.txt")
        downloaded_files = {}
        
        # Read existing log to check for downloaded files
        if os.path.exists(daily_index_log) and os.path.getsize(daily_index_log) > 0:
            try:
                with open(daily_index_log, 'r') as log:
                    for line in log:
                        parts = line.strip().split(',')
                        if len(parts) == 4:
                            downloaded_files[parts[1]] = parts[3]
            except IOError as e:
                print(f"Error reading log file: {e}")
        else:
            print("Log file is empty or does not exist.")

        # Determine current quarter and year
        current_year = end_date.year
        current_quarter = (end_date.month - 1) // 3 + 1
        
        # Set start date for the current quarter
        start_date = datetime(current_year, (current_quarter - 1) * 3 + 1, 1)
        
        zip_directory = EDGAR_SOURCE_DIR
        
        os.makedirs(zip_directory, exist_ok=True)

        zip_path = os.path.join(zip_directory, f"{current_year}-QTR{current_quarter}.zip")
        master_idx_file = f"{current_year}-QTR{current_quarter}.idx"  # Name for the master index file

        skip_dates = [datetime(2024, 7, 3), datetime(2024, 7, 4), datetime(2024, 9, 2)]

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            master_idx_content = []
            current_date = max(start_date, datetime(2024, 7, 1))
            total_days = (end_date - current_date).days + 1
            pbar = tqdm(total=total_days, desc="Downloading Daily Index", unit="files")

            while current_date <= end_date:
                if current_date.weekday() >= 5 or current_date in skip_dates:
                    current_date += timedelta(days=1)
                    pbar.update(1)
                    continue
                
                file_name = f"master.{current_date.strftime('%Y%m%d')}.idx"
                if file_name in downloaded_files:
                    current_date += timedelta(days=1)
                    pbar.update(1)
                    continue

                url = f"{daily_base_url}{current_date.year}/QTR{(current_date.month-1)//3+1}/{file_name}"
                max_attempts = 3
                print(f"Attempting to download {url}")
                for attempt in range(max_attempts):
                    try:
                        headers = {'User-Agent': "FORTHELULZ@anonops.com"}
                        req = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(req, timeout=3) as response:
                            if response.getcode() == 200:
                                content = response.read()
                                file_size = len(content)
                                file_hash = hashlib.sha256(content).hexdigest()
                                print(f"Successfully downloaded {file_name}. Size: {file_size} bytes. Hash: {file_hash}")

                                # Decode content here to avoid reading twice
                                idx_content = content.decode('utf-8').split('\n')
                                if not master_idx_content:
                                    print("Setting up master index header.")
                                    master_idx_content = idx_content[:11]
                                master_idx_content.extend(idx_content[11:])

                                # Log the download
                                with open(daily_index_log, 'a') as log:
                                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    log.write(f"{timestamp},{file_name},{file_size},{file_hash}\n")
                                print(f"Logged download of {file_name}")
                                break
                            else:
                                print(f"Failed to download {file_name}. Status: {response.getcode()}")
                    except (urllib.error.HTTPError, urllib.error.URLError) as e:
                        print(f"Attempt {attempt + 1} failed: {e}")
                        if attempt < max_attempts - 1:
                            time.sleep(1)  # Delay before retry
                        else:
                            print(f"Max attempts reached for {file_name}. Moving on.")

                current_date += timedelta(days=1)
                pbar.update(1)

            # Write the master index content to the zip file
            if master_idx_content:
                print("Writing master index to ZIP file...")
                zipf.writestr(master_idx_file, '\n'.join(master_idx_content))
                print(f"Master index file {master_idx_file} written to {zip_path}")

        pbar.close()
        print(f"\nDaily index files up to {end_date.strftime('%Y-%m-%d')} have been processed and saved to {zip_path}.")

    # Main execution within download_edgar_archives
    if check_free_space():
        print("Enough disk space available. Proceeding with downloads.")
        download_edgar_files()
    else:
        print("Not enough disk space. Downloads aborted.")

    print("EDGAR archives download process completed.")
def edgar_second():
    global failed_downloads, EDGAR_SOURCE_DIR
    gamecat_ascii()
    
    def search_master_archives(search_term, directory):
        search_term = search_term.strip()
        if not search_term or ' ' in search_term:
            print("Invalid search term provided. Please enter a single term.")
            return

        # Ensure the output directory exists
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        results_file = os.path.join(directory, f"{search_term}_edgar_results.csv")
        zip_files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(".zip")]

        with open(results_file, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["CIK", "Company Name", "Form Type", "Date Filed", "Filename"])

            # Wrap the iterable with tqdm for a progress bar
            for zip_path in tqdm(zip_files, desc="Searching", unit="file"):
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_file:
                        for zip_info in zip_file.infolist():
                            if zip_info.filename.endswith(".idx"):
                                with zip_file.open(zip_info) as idx_file:
                                    raw_data = idx_file.read()
                                    encoding = chardet.detect(raw_data)['encoding']
                                    lines = raw_data.decode(encoding, errors='replace').splitlines()
                                    for line in lines:
                                        parts = line.split('|')
                                        if len(parts) < 5:
                                            continue
                                        company_name = parts[1].strip()
                                        if search_term.lower() in company_name.lower():
                                            csv_writer.writerow(parts)
                except Exception as e:
                    print(f"Error processing file {zip_path}: {e}")

        if os.path.exists(results_file) and os.path.getsize(results_file) > 0:
            print(f"Search results saved to {results_file}")
        else:
            print(f"No results found for '{search_term}'")
            if os.path.exists(results_file):
                os.remove(results_file)

    def get_valid_search_term():
        forbidden_terms = {'a', 'b', 'c', 'edgar', 'www', 'https', '*', '**'}
        special_terms = {'gamestop', 'cohen', 'chewy'}
        deep_value_terms = {'citi', 'citigroup', 'salomon', 'lehman', 'stearns', 'barney', 
                            'smith', 'stanley', 'traveler', 'wamu', 'jpm', 'buffet', 
                            'goldman', 'ubs', 'suisse', 'nomura'}
        while True:
            search_term = input("Enter search term: ").strip().lower()
            if len(search_term) == 1 or search_term.isdigit():
                return None
            if not search_term:
                print("why did you enter a blank query? c'mon.")
                continue

            if (len(search_term) == 1 and search_term.isalnum()) or search_term in forbidden_terms:
                print("anon, don't fucking search for that. c'mon.")
                
                if search_term in forbidden_terms:
                    confirmation = input("THIS IS NOT A GOOD IDEA. YOU SURE? (y/n): ").strip().lower()
                    if confirmation == 'y':
                        return search_term
                    else:
                        continue

            if search_term in deep_value_terms:
                print("DOING SOME DEEP FUCKING VALUE DILIGENCE? CAN DO ANON.")
                return search_term

            if search_term in special_terms:
                if search_term == 'gamestop' or search_term == 'cohen':
                    print("POWER TO THE PLAYERS!")
                elif search_term == 'chewy':
                    print("CHEWY. INVESTMENT ADVICE THAT STICKS")
                return search_term

            if search_term == 'gill':
                print("ONE GILL IS NOT LIKE THE OTHERS. ONE IS NOT A CAT.")
                return search_term

            return search_term

    def search_and_prompt():
        if not failed_downloads:
            print("All files downloaded successfully.")
            while True:
                search_term = get_valid_search_term()
                if search_term:
                    search_master_archives(search_term, EDGAR_SOURCE_DIR)
                    another_search = input("Would you like to search for another term? (yes/no): ").strip().lower()
                    if another_search not in ["yes", "y"]:
                        print("Game On Anon")
                        break
                else:
                    print("Search term cannot be empty..")
        else:
            print("Some files failed to download. Please check the error list.")

    # Run the search and prompt logic in a separate thread
    search_thread = threading.Thread(target=search_and_prompt)
    search_thread.start()
    search_thread.join()  # Wait for the thread to complete
def edgar_third(csv_file, method):
    def download_from_csv(csv_file):
        base_url = "https://www.sec.gov/Archives/"
        base_download_dir = EDGAR_SOURCE_DIR
        headers = {'User-Agent': "anonymous/FORTHELULZ@anonyops.com"}
        retries = 3
        delay = 1
        full_csv_path = os.path.join(base_download_dir, csv_file)
        
        with open(full_csv_path, newline='', encoding='utf-8') as csvfile:
            total_rows = sum(1 for row in csv.reader(csvfile)) - 1  # Subtract 1 for header
        
        with open(full_csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)  # Skip header
            rows = list(reader)
            if 'Download Location' not in header:
                header.append('Download Location')
            
            pbar = tqdm(total=total_rows, desc="Downloading", unit="file")
            failed_downloads = []
            
            for row in rows:
                if len(row) < 5:
                    pbar.update(1)
                    continue
                
                cik = row[0]
                relative_url = row[4]  # Filename column
                url = base_url + relative_url.lstrip('/')
                filename = os.path.basename(url)
                cik_dir = os.path.join(base_download_dir, cik)
                os.makedirs(cik_dir, exist_ok=True)
                full_path = os.path.join(cik_dir, filename)
                
                download_success = False
                for attempt in range(retries):
                    try:
                        req = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(req, timeout=10) as response:
                            if response.getcode() != 200:
                                raise HTTPError(url, response.getcode(), "Non-200 status code", headers, None)
                            with open(full_path, 'wb') as file:
                                file.write(response.read())
                            download_success = True
                            break
                    except (HTTPError, URLError, IOError) as e:
                        print(f"Attempt {attempt + 1} failed: {e}")
                        if attempt < retries - 1:
                            time.sleep(delay * (2 ** attempt))
                
                if download_success:
                    row.append(full_path)
                else:
                    failed_downloads.append(url)
                    row.append('Failed')
                
                pbar.update(1)
            
            pbar.close()
        
        with open(full_csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(rows)

        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        html_file_name = f"{base_name}_index.html"
        with open(html_file_name, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write('<!DOCTYPE html><html><head><title>Download Index</title></head><body><table border="1">')
            htmlfile.write('<tr>' + ''.join(f'<th>{h}</th>' for h in header) + '</tr>')
            for row in rows:
                htmlfile.write('<tr>')
                for item in row:
                    if item.startswith('./edgar') or item == 'Failed':
                        htmlfile.write(f'<td><a href="file://{os.path.abspath(item)}">{item}</a></td>' if item != 'Failed' else f'<td>{item}</td>')
                    else:
                        htmlfile.write(f'<td>{item}</td>')
                htmlfile.write('</tr>')
            htmlfile.write('</table></body></html>')
        print(f"HTML index created: {html_file_name}")

    def download_from_crawling(csv_file):
        base_download_dir = EDGAR_SOURCE_DIR
        ciks = set()
        full_csv_path = os.path.join(base_download_dir, csv_file)
        print(f"Attempting to read CSV from: {full_csv_path}")  # Debug path

        if not os.path.exists(full_csv_path):
            print(f"CSV file not found: {full_csv_path}")
            return

        with open(full_csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip header
            for row in reader:
                print(f"Processing row: {row}")  # Debug row content
                if len(row) > 0 and row[0].isdigit() and 1 <= len(row[0]) <= 10:
                    ciks.add(row[0])
                else:
                    print(f"Skipping invalid CIK row: {row}")

        if not ciks:
            print(f"No valid CIKs found in {csv_file}. Check CSV format or content.")
            return

        print(f"Extracted CIKs: {ciks}")  # Debug extracted CIKs

        def fetch_directory(url):
            retries = 3
            delay = 1
            headers = {'User-Agent': "anonymous/FORTHELULZ@anonyops.com"}
            for attempt in range(retries):
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.getcode() != 200:
                            raise HTTPError(url, response.getcode(), "Non-200 status code", headers, None)
                        time.sleep(delay)
                        return BeautifulSoup(response.read(), 'html.parser')
                except (HTTPError, URLError) as e:
                    print(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt < retries - 1:
                        time.sleep(delay * (attempt + 1))
            raise Exception(f"Failed to fetch {url} after {retries} retries")

        def scrape_subdirectories(sec_url):
            soup = fetch_directory(sec_url)
            rows = soup.find_all('a', href=True)
            subdirectories = []
            for row in rows:
                href = row['href']
                # Filter for 18-digit subdirectory IDs under /data/{CIK}/
                if (href and len(href.strip('/').split('/')[-1]) == 18 and 
                    href.startswith(f'/Archives/edgar/data/{sec_url.split("/")[-2]}/')):
                    subdirectories.append(href.strip('/').split('/')[-1])
            print(f"Scraped subdirectories: {subdirectories}")
            return subdirectories

        def download_file(url, directory, retries=3, delay=1):
            for attempt in range(retries):
                try:
                    headers = {'User-Agent': "anonymous/FORTHELULZ@anonyops.com"}
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.getcode() != 200:
                            raise HTTPError(url, response.getcode(), "Non-200 status code", headers, None)
                        filename = os.path.join(directory, os.path.basename(url))
                        with open(filename, 'wb') as file:
                            file.write(response.read())
                        print(f"Downloaded: {filename}")
                        return True
                except (HTTPError, URLError) as e:
                    print(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt < retries - 1:
                        time.sleep(delay * (attempt + 1))
            print(f"Failed to download {url} after {retries} retries")
            return False

        os.makedirs(base_download_dir, exist_ok=True)
        header = ['CIK', 'URL', 'Download Location', 'Status']
        rows = []

        def process_cik(cik):
            sec_url_full = f"https://www.sec.gov/Archives/edgar/data/{cik}/"  # Correct base URL
            print(f"Embarking on the quest for {sec_url_full}...")
            folder_name = sec_url_full.rstrip('/').split('/')[-1]
            full_download_directory = os.path.join(base_download_dir, folder_name)
            os.makedirs(full_download_directory, exist_ok=True)
            print(f"Full download directory: {full_download_directory}")

            subdirectories = scrape_subdirectories(sec_url_full)
            if not subdirectories:
                print(f"No subdirectories found at {sec_url_full}.")
                return

            full_subdirectory_urls = [f"{sec_url_full.rstrip('/')}/{sub}" for sub in subdirectories]
            for subdirectory in full_subdirectory_urls:
                try:
                    soup = fetch_directory(subdirectory)
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        # Focus on .txt files, with .htm/.html for forms as secondary
                        if href.endswith('.txt') or (href.endswith(('.htm', '.html')) and 'form' in href.lower()):
                            full_url = "https://www.sec.gov" + href if href.startswith('/') else subdirectory + '/' + href
                            print(f"Attempting to download: {full_url}")
                            download_success = download_file(full_url, full_download_directory)
                            download_location = os.path.join(full_download_directory, os.path.basename(full_url)) if download_success else 'Failed'
                            rows.append([cik, full_url, download_location, 'Success' if download_success else 'Failed'])
                except Exception as e:
                    print(f"Error processing {subdirectory}: {e}")

        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(process_cik, ciks)

        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(rows)

        html_file_name = os.path.splitext(csv_file)[0] + '_index.html'
        with open(html_file_name, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write('<!DOCTYPE html><html><head><title>Download Index</title></head><body><table border="1">')
            htmlfile.write('<tr>' + ''.join(f'<th>{h}</th>' for h in header) + '</tr>')
            for row in rows:
                htmlfile.write('<tr>')
                for item in row:
                    if item.startswith('./edgar') or item == 'Failed':
                        htmlfile.write(f'<td><a href="file://{os.path.abspath(item)}">{item}</a></td>' if item != 'Failed' else f'<td>{item}</td>')
                    else:
                        htmlfile.write(f'<td><a href="{item}">{item}</a></td>')
                htmlfile.write('</tr>')
            htmlfile.write('</table></body></html>')
        print(f"Quest completed for {len(ciks)} CIKs. CSV updated and HTML index created.")

    if method == 'url':
        download_from_csv(csv_file)
    elif method == 'crawl':
        download_from_crawling(csv_file)
    else:
        print("Unknown method for CSV extraction.")

def process_cik(cik, rows=None, base_download_dir='./EDGAR/DATA'):
    if rows is None:
        rows = []
    sec_url_full = f"https://www.sec.gov/Archives/edgar/data/{cik}/"
    print(f"Embarking on the quest for {sec_url_full}...")
    folder_name = sec_url_full.rstrip('/').split('/')[-1]
    full_download_directory = os.path.join(base_download_dir, folder_name)
    print(f"Full download directory: {full_download_directory} - Here lies our treasure vault")

    subdirectories = scrape_subdirectories(sec_url_full)
    if not subdirectories:
        print(f"No hidden chambers found at {sec_url_full}. Exiting this quest.")
        return

    full_subdirectory_urls = [f"{sec_url_full.rstrip('/')}/{sub}" for sub in subdirectories]
    
    sanitized_file_path = 'sanitized_subdirectories.txt'
    with open(sanitized_file_path, 'w') as sanitized_file:
        sanitized_file.write('\n'.join(full_subdirectory_urls))
    print(f"Sanitized list created: {sanitized_file_path} - The map to hidden chambers is drawn")

    output_file_path = 'completed_subdirectories.txt'
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as file:
            completed_subdirectories = [line.strip() for line in file]
    else:
        completed_subdirectories = []

    os.makedirs(full_download_directory, exist_ok=True)
    print(f"Download directory created: {full_download_directory} - The vault is ready to receive its riches")

    total_subdirectories = len(full_subdirectory_urls)
    processed_subdirectories = len(completed_subdirectories)

    for subdirectory in full_subdirectory_urls:
        if subdirectory in completed_subdirectories:
            print(f"Skipping already plundered chamber: {subdirectory}")
            continue

        print(f"Venturing into the chamber: {subdirectory}")
        try:
            soup = fetch_directory(subdirectory)
            links = soup.find_all('a')
            txt_links = [link.get('href') for link in links if link.get('href') and link.get('href').endswith('.txt')]
            print(f"Found txt links in {subdirectory}: {txt_links} - Scrolls of lore discovered")
            for txt_link in txt_links:
                txt_url = "https://www.sec.gov" + txt_link
                print(f"Downloading txt file: {txt_url} - Securing the scroll")
                download_success = download_file(txt_url, full_download_directory)
                download_location = os.path.join(full_download_directory, os.path.basename(txt_url)) if download_success else 'Failed'
                rows.append([cik, txt_url, download_location, 'Success' if download_success else 'Failed'])
                if download_success:
                    with open(output_file_path, 'a') as completed_file:
                        completed_file.write(subdirectory + '\n')
                    break
                time.sleep(0.1)
        except Exception as e:
            print(f"Failed to access {subdirectory}: {e} - Beware, for this path is cursed!")
            with open('error_log.txt', 'a') as error_log_file:
                error_log_file.write(f"Failed to access {subdirectory}: {e}\n")

        processed_subdirectories += 1
        print(f"Progress: {processed_subdirectories}/{total_subdirectories} chambers explored.")

    remaining_subdirectories = [sub for sub in full_subdirectory_urls if sub not in completed_subdirectories]
    with open(sanitized_file_path, 'w') as sanitized_file:
        sanitized_file.write('\n'.join(remaining_subdirectories))

    print("Download complete for current CIK - The quest for this treasure trove ends.")
def fetch_directory(url):
    retries=3
    delay=1
    verbose=True
    headers = {
        'User-Agent': "anonymous/FORTHELULZ@anonyops.com"  # Assuming you've defined this header elsewhere
    }
    
    for attempt in range(retries):
        try:
            print(f"Fetching URL: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() != 200:
                    raise HTTPError(url, response.getcode(), "Non-200 status code", headers, None)
                time.sleep(delay)  # Slow down to avoid rate limiting
                # Here we read the content and then parse it with BeautifulSoup
                content = response.read()
                return BeautifulSoup(content, 'html.parser')
        except (HTTPError, URLError) as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retries - 1:  # No sleep til brooklyn
                time.sleep(delay * (attempt + 1))  # Exponential backoff
    raise Exception(f"Failed to fetch {url} after {retries} retries")
def scrape_subdirectories(sec_url):
    soup = fetch_directory(sec_url)
    rows = soup.find_all('a')
    subdirectories = []
    for row in rows:
        href = row.get('href')
        # Check if the href is a subdirectory link with 18-digit numeric names
        if href and href.startswith('/Archives/edgar/data/') and len(href.strip('/').split('/')[-1]) == 18:
            subdirectories.append(href.strip('/').split('/')[-1])
        else:
            print(f"Skipping non-matching href: {href}")  # Log non-matching hrefs for debugging
    print(f"Scraped subdirectories: {subdirectories}\n ")
    return subdirectories
def extract_txt_links(soup):
    links = soup.find_all('a')
    txt_links = [link.get('href') for link in links if link.get('href') and link.get('href').endswith('.txt')]
    return txt_links
def download_file(url, directory, retries=3, delay=1):
    # The spell to conjure a file from the digital ether
    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': "anonymous/FORTHELULZ@anonyops.com"
            }                    
            print(f"Attempting to download {url}...")
            # The spell to conjure a file from the digital ether
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() != 200:
                    raise HTTPError(url, response.getcode(), "Non-200 status code", headers, None)
                file_content = response.read()  # Store the file content

                filename = os.path.join(directory, os.path.basename(url))
                with open(filename, 'wb') as file:
                    file.write(response.read())  # Changed from response.content to response.read()
                print(f"Downloaded: {filename}")
                md5_hash = hashlib.md5(file_content).hexdigest()
                timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                log_filename = os.path.join(directory, os.path.splitext(os.path.basename(url))[0] + '-legal-source-log.txt')
                with open(log_filename, 'w') as log_file:
                    log_file.write(f"URL: {url}\nDownloaded at: {timestamp},\n{filename} with MD5 :{md5_hash}\n")
                print(f"Logged download details to {log_filename}")
                file_size = os.path.getsize(filename)
                print(f"File size: {file_size} bytes - the weight of this digital artifact")
                return True

        except (HTTPError, URLError) as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e} - A dragon guards this treasure!")
            if attempt < retries - 1:  # No need to sleep after the last attempt
                time.sleep(delay * (attempt + 1))
    print(f"Failed to download {url} after {retries} retries - The treasure remains elusive")
    return False
def process_cik(cik):
    # The URL where our quest begins
    sec_url_full = f"https://www.sec.gov/Archives/edgar/data/{cik}/"
    print(f"Embarking on the quest for {sec_url_full}...")
    base_download_dir = './EDGAR/DATA'
    folder_name = sec_url_full.rstrip('/').split('/')[-1]
    full_download_directory = os.path.join(base_download_dir, folder_name)
    print(f"Full download directory: {full_download_directory} - Here lies our treasure vault")

    # Here we call upon the ancient rites to reveal hidden paths
    subdirectories = scrape_subdirectories(sec_url_full)
    if not subdirectories:
        print(f"No hidden chambers found at {sec_url_full}. Exiting this quest.")
        return  # Exit function instead of using continue in a loop

    full_subdirectory_urls = [f"{sec_url_full.rstrip('/')}/{sub}" for sub in subdirectories]
    
    sanitized_file_path = 'sanitized_subdirectories.txt'
    with open(sanitized_file_path, 'w') as sanitized_file:
        sanitized_file.write('\n'.join(full_subdirectory_urls))
    print(f"Sanitized list created: {sanitized_file_path} - The map to hidden chambers is drawn")

    output_file_path = 'completed_subdirectories.txt'
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as file:
            completed_subdirectories = [line.strip() for line in file]
    else:
        completed_subdirectories = []

    os.makedirs(full_download_directory, exist_ok=True)
    print(f"Download directory created: {full_download_directory} - The vault is ready to receive its riches")

    total_subdirectories = len(full_subdirectory_urls)
    processed_subdirectories = len(completed_subdirectories)

    rows = []  # Initialize rows list here
    for subdirectory in full_subdirectory_urls:
        if subdirectory in completed_subdirectories:
            print(f"Skipping already plundered chamber: {subdirectory}")
            continue

        print(f"Venturing into the chamber: {subdirectory}")
        try:
            # Summoning the directory's content with an ancient spell
            soup = fetch_directory(subdirectory)
            # Extracting the scrolls of knowledge from the chamber
            txt_links = extract_txt_links(soup)
            print(f"Found txt links in {subdirectory}: {txt_links} - Scrolls of lore discovered")
            for txt_link in txt_links:
                txt_url = "https://www.sec.gov" + txt_link
                print(f"Downloading txt file: {txt_url} - Securing the scroll")
                download_success = download_file(txt_url, full_download_directory)
                download_location = os.path.join(full_download_directory, os.path.basename(txt_url)) if download_success else 'Failed'
                rows.append([cik, txt_url, download_location, 'Success' if download_success else 'Failed'])
                if download_success:
                    with open(output_file_path, 'a') as completed_file:
                        completed_file.write(subdirectory + '\n')
                    break
                time.sleep(0.1)  # A brief rest to avoid angering the digital spirits
        except Exception as e:
            print(f"Failed to access {subdirectory}: {e} - Beware, for this path is cursed!")
            with open('error_log.txt', 'a') as error_log_file:
                error_log_file.write(f"Failed to access {subdirectory}: {e}\n")

        processed_subdirectories += 1
        print(f"Progress: {processed_subdirectories}/{total_subdirectories} chambers explored.")

    remaining_subdirectories = [sub for sub in full_subdirectory_urls if sub not in completed_subdirectories]

    with open(sanitized_file_path, 'w') as sanitized_file:
        sanitized_file.write('\n'.join(remaining_subdirectories))

    print("Download complete for current CIK - The quest for this treasure trove ends.")
    return rows  # Return the rows for further processing if needed
def download_archives(source_dir, filelist_path, urls):
    # Ensure the directory exists
    print(f"Ensuring directory {source_dir} exists...")
    os.makedirs(source_dir, exist_ok=True)
    print(f"Directory {source_dir} created or already exists.")

    # Verbose step: Checking local files
    print("Checking existing local files...")
    existing_files = {}
    if os.path.exists(filelist_path):
        with open(filelist_path, 'r') as filelist:
            for line in filelist:
                parts = line.strip().split(',')
                if len(parts) == 4:
                    existing_files[parts[1]] = {
                        'size': int(parts[3]),
                        'timestamp': datetime.strptime(parts[2], '%Y-%m-%d %H:%M:%S')
                    }
    print(f"Checked {len(existing_files)} existing files.")

    # Counters for status
    total_attempts = 0
    failures = 0
    successes = 0
    skips = 0

    def download_and_record(url):
        nonlocal total_attempts, failures, successes, skips
        file_name = url.split('/')[-1]
        output_path = os.path.join(source_dir, file_name)

        # Check if the file exists and matches size in filelist.txt
        if output_path in existing_files:
            local_size = os.path.getsize(output_path) if os.path.exists(output_path) else -1
            if local_size == existing_files[output_path]['size']:
                print(f"Skipping download of {url}, local file size matches.")
                skips += 1
                return

        total_attempts += 1
        attempts = 0
        max_attempts = 3  # Max retries

        while attempts < max_attempts:
            print(f"Attempting to download {url}, attempt {attempts + 1}")
            headers = {'User-Agent': "FORTHELULZ@anonyops.com"}
            try:
                # Add delay to ensure we don't exceed 10 requests per second with 8 threads
                time.sleep(0.8)  # 0.8 seconds delay per thread; 8 threads * 0.8 = 6.4 seconds per cycle, which is under 10 requests per second
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    if response.getcode() == 200:
                        with open(output_path, "wb") as file:
                            file.write(response.read())
                        print(f"File from {url} downloaded on attempt {attempts + 1} and saved as {output_path}")
                        successes += 1
                        break  
                    elif response.getcode() == 403:
                        print(f"Access denied for {url} on attempt {attempts + 1}, trying fallback User-Agent.")
                        fallback_headers = {'User-Agent': "anonymous/FORTHELULZ@anonyops.com"}
                        fallback_req = urllib.request.Request(url, headers=fallback_headers)
                        with urllib.request.urlopen(fallback_req) as fallback_response:
                            if fallback_response.getcode() == 200:
                                with open(output_path, "wb") as file:
                                    file.write(fallback_response.read())
                                print(f"File from {url} downloaded with fallback on attempt {attempts + 1} and saved as {output_path}")
                                successes += 1
                                break  
                    else:
                        print(f"Failed to download file from {url} on attempt {attempts + 1}. Status code: {response.getcode()}")
                attempts += 1
            except (urllib.error.HTTPError, urllib.error.URLError, IOError) as e:
                print(f"Error occurred for {url} on attempt {attempts + 1}: {e}")
                attempts += 1

            if attempts == max_attempts:
                failures += 1
                print(f"Failed to download {url} after {max_attempts} attempts.")
                    
        if os.path.exists(output_path):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_size = os.path.getsize(output_path)
            with open(filelist_path, 'a') as filelist:
                filelist.write(f"{url},{output_path},{timestamp},{file_size}\n")
            
            logging.info(f"Successfully downloaded and recorded: {output_path}")

    # Verbose step: Beginning downloads
    print("Beginning downloads...")
    with ThreadPoolExecutor(max_workers=4) as executor: 
        futures = [executor.submit(download_and_record, url) for url in urls]
        for future in tqdm(futures, total=len(urls), desc="Overall Download Progress", unit="files"):
            future.result()  # Wait for each task to complete

    print(f"\nDownload Summary:")
    print(f"Total Attempts: {total_attempts}")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print(f"Skips: {skips}")
def process_zips(url, max_retries=3, timeout=10):
    OUTPUT_DIR = os.path.join(ROOT_DIR, "SecNport")  # Adjust based on which archives you're processing
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            file_size = int(response.headers.get('Content-Length', 0))
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=os.path.basename(url), leave=False) as bar:
                content = b''
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        content += chunk
                        bar.update(len(chunk))
            zip_filename = os.path.basename(url)
            local_path = os.path.join(OUTPUT_DIR, zip_filename)
            with open(local_path, 'wb') as file:
                file.write(content)
            print(f"Successfully downloaded: {zip_filename}")
            
            file_size = os.path.getsize(local_path)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(FILELIST, 'a') as filelist:
                filelist.write(f"{url},{local_path},{timestamp},{file_size}\n")
            return local_path
        except requests.RequestException as e:
            print(f"Download attempt {attempt + 1} failed for {url}: {e}")
            if attempt == max_retries - 1:
                print(f"Max retries reached for {url}, skipping.")
                return None
            time.sleep(2 ** attempt)
    return None
def process_tsv_file(tsv_name, row, zip_file, verbose=False):
    """Process a single TSV file for a given row and return enriched holding_summary with all fields."""
    import zipfile
    import pandas as pd
    import logging

    def log_safe(msg):
        if verbose:
            logging.info(msg)

    holding_summary = {}
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            with zip_ref.open(f'{tsv_name}.tsv') as tsvfile:
                df = pd.read_csv(tsvfile, delimiter='\t', low_memory=False, encoding='utf-8', on_bad_lines='skip')
                match_col = 'ACCESSION_NUMBER' if tsv_name != 'IDENTIFIERS' else 'HOLDING_ID'
                match_value = row['ACCESSION_NUMBER'] if tsv_name != 'IDENTIFIERS' else row['HOLDING_ID']
                if tsv_name in ['SUBMISSION', 'REGISTRANT', 'FUND_REPORTED_INFO', 'INTEREST_RATE_RISK', 'BORROWER',
                               'BORROW_AGGREGATE', 'MONTHLY_TOTAL_RETURN']:
                    match_row = df[df[match_col] == match_value] if match_col in df.columns else pd.DataFrame()
                elif tsv_name == 'MONTHLY_RETURN_CAT_INSTRUMENT':
                    match_row = df[(df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']) & 
                                  (df['ASSET_CAT'] == row['ASSET_CAT'])] if 'ASSET_CAT' in df.columns else pd.DataFrame()
                elif tsv_name == 'IDENTIFIERS':
                    match_row = df[df[match_col] == match_value] if match_col in df.columns else pd.DataFrame()

                if not match_row.empty:
                    for col in match_row.columns:
                        prefixed_col = f"{tsv_name}_{col}"
                        holding_summary[prefixed_col] = match_row.iloc[0][col]
                    log_safe(f"Matched {tsv_name} for {match_col} {match_value}")
                else:
                    log_safe(f"No match for {tsv_name} with {match_col} {match_value}")
    except Exception as e:
        log_safe(f"Error processing {tsv_name}.tsv in {zip_file}: {str(e)}")
    return holding_summary
def search_nport_swaps(zip_file, search_terms, verbose=False, debug=False, log_file=None):
    import os
    import zipfile
    import pandas as pd
    import tqdm
    from datetime import datetime
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import logging

    summary = []
    
    if verbose and log_file:
        log_dir = os.path.dirname(log_file) or '.'
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', filemode='a')
    
    def log_safe(msg):
        if verbose:
            logging.info(msg)
    
    log_safe(f"Starting {zip_file}")
    
    try:
        base_name = os.path.basename(zip_file)
        year = base_name[:4]
        quarter_char = base_name[4]
        quarter = {'q': 1, '1': 1, 'w': 2, '2': 2, 'e': 3, '3': 3, 'r': 4, '4': 4}.get(quarter_char.lower(), None)

        if quarter is not None:
            quarter_start_date = datetime(int(year), quarter*3 - 2, 1)
            timestamp = int(quarter_start_date.timestamp())
        else:
            timestamp = None
            log_safe(f"Warning: Could not parse quarter from {zip_file}")
            return summary

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            if 'FUND_REPORTED_HOLDING.tsv' not in zip_ref.namelist():
                log_safe(f"Warning: {zip_file} does not contain FUND_REPORTED_HOLDING.tsv")
                return summary

            chunksize = 100000
            with zip_ref.open('FUND_REPORTED_HOLDING.tsv') as tsvfile:
                total_rows = sum(1 for _ in tsvfile)
                tsvfile.seek(0)

            with tqdm.tqdm(total=total_rows, desc=f"Processing {zip_file}", unit="row") as pbar:
                for chunk in pd.read_csv(zip_ref.open('FUND_REPORTED_HOLDING.tsv'), delimiter='\t', chunksize=chunksize,
                                       low_memory=False, encoding='utf-8', on_bad_lines='skip'):
                    if 'FILENAME_TIMESTAMP' not in chunk.columns:
                        chunk['FILENAME_TIMESTAMP'] = timestamp

                    string_columns = ['ISSUER_NAME', 'ISSUER_TITLE', 'ACCESSION_NUMBER', 'HOLDING_ID', 'ISSUER_LEI',
                                     'ISSUER_CUSIP', 'UNIT', 'OTHER_UNIT_DESC', 'CURRENCY_CODE', 'PAYOFF_PROFILE',
                                     'ASSET_CAT', 'OTHER_ASSET', 'ISSUER_TYPE', 'OTHER_ISSUER', 'INVESTMENT_COUNTRY',
                                     'IS_RESTRICTED_SECURITY', 'FAIR_VALUE_LEVEL', 'DERIVATIVE_CAT']
                    chunk[string_columns] = chunk[string_columns].fillna('').astype(str)
                    
                    def contains_search_term(row):
                        for term in search_terms:
                            for col in string_columns:
                                if pd.notna(row[col]) and term.lower() in str(row[col]).lower():
                                    return True
                        return False
                    
                    keyword_holdings = chunk[chunk.apply(contains_search_term, axis=1)]
                    log_safe(f"Processed chunk with {len(chunk)} rows, found {len(keyword_holdings)} matches for {', '.join(search_terms)} in {zip_file}")

                    if not keyword_holdings.empty:
                        tsv_files = ['SUBMISSION', 'REGISTRANT', 'FUND_REPORTED_INFO', 'INTEREST_RATE_RISK', 'BORROWER',
                                    'BORROW_AGGREGATE', 'MONTHLY_TOTAL_RETURN', 'MONTHLY_RETURN_CAT_INSTRUMENT', 'IDENTIFIERS']
                        
                        with ProcessPoolExecutor() as executor:
                            for index, row in keyword_holdings.iterrows():
                                holding_summary = {
                                    'ACCESSION_NUMBER': row['ACCESSION_NUMBER'] if 'ACCESSION_NUMBER' in row else None,
                                    'HOLDING_ID': row['HOLDING_ID'] if 'HOLDING_ID' in row else None,
                                    'FILENAME_TIMESTAMP': timestamp,
                                    'FILING_DATE': None,  # To be populated from SUBMISSION_FILING_DATE
                                    'ISSUER_NAME': row['ISSUER_NAME'] if 'ISSUER_NAME' in row else None,
                                    'ISSUER_LEI': row['ISSUER_LEI'] if 'ISSUER_LEI' in row else None,
                                    'ISSUER_TITLE': row['ISSUER_TITLE'] if 'ISSUER_TITLE' in row else None,
                                    'ISSUER_CUSIP': row['ISSUER_CUSIP'] if 'ISSUER_CUSIP' in row else None,
                                    'BALANCE': row['BALANCE'] if 'BALANCE' in row else None,
                                    'UNIT': row['UNIT'] if 'UNIT' in row else None,
                                    'OTHER_UNIT_DESC': row['OTHER_UNIT_DESC'] if 'OTHER_UNIT_DESC' in row else None,
                                    'CURRENCY_CODE': row['CURRENCY_CODE'] if 'CURRENCY_CODE' in row else None,
                                    'CURRENCY_VALUE': row['CURRENCY_VALUE'] if 'CURRENCY_VALUE' in row else None,
                                    'EXCHANGE_RATE': row['EXCHANGE_RATE'] if 'EXCHANGE_RATE' in row else None,
                                    'PERCENTAGE': row['PERCENTAGE'] if 'PERCENTAGE' in row else None,
                                    'PAYOFF_PROFILE': row['PAYOFF_PROFILE'] if 'PAYOFF_PROFILE' in row else None,
                                    'ASSET_CAT': row['ASSET_CAT'] if 'ASSET_CAT' in row else None,
                                    'OTHER_ASSET': row['OTHER_ASSET'] if 'OTHER_ASSET' in row else None,
                                    'ISSUER_TYPE': row['ISSUER_TYPE'] if 'ISSUER_TYPE' in row else None,
                                    'OTHER_ISSUER': row['OTHER_ISSUER'] if 'OTHER_ISSUER' in row else None,
                                    'INVESTMENT_COUNTRY': row['INVESTMENT_COUNTRY'] if 'INVESTMENT_COUNTRY' in row else None,
                                    'IS_RESTRICTED_SECURITY': row['IS_RESTRICTED_SECURITY'] if 'IS_RESTRICTED_SECURITY' in row else None,
                                    'FAIR_VALUE_LEVEL': row['FAIR_VALUE_LEVEL'] if 'FAIR_VALUE_LEVEL' in row else None,
                                    'DERIVATIVE_CAT': row['DERIVATIVE_CAT'] if 'DERIVATIVE_CAT' in row else None,
                                }

                                # Parallel TSV processing
                                futures = [executor.submit(process_tsv_file, tsv_name, row, zip_file, verbose) 
                                          for tsv_name in tsv_files]
                                for future in as_completed(futures):
                                    tsv_data = future.result()
                                    holding_summary.update(tsv_data)

                                # Populate FILING_DATE from SUBMISSION
                                if 'SUBMISSION_FILING_DATE' in holding_summary:
                                    holding_summary['FILING_DATE'] = pd.to_datetime(holding_summary['SUBMISSION_FILING_DATE'], format='%d-%b-%Y', errors='coerce')

                                # Derive YYYYQQ from SUBMISSION_REPORT_ENDING_PERIOD
                                if 'SUBMISSION_REPORT_ENDING_PERIOD' in holding_summary:
                                    report_date = pd.to_datetime(holding_summary['SUBMISSION_REPORT_ENDING_PERIOD'], format='%d-%b-%Y', errors='coerce')
                                    if not pd.isna(report_date):
                                        holding_summary['YYYYQQ'] = f"{report_date.year}Q{((report_date.month-1)//3) + 1}"
                                    else:
                                        holding_summary['YYYYQQ'] = None
                                elif 'FUND_REPORTED_INFO_REPORT_DATE' in holding_summary:
                                    report_date = pd.to_datetime(holding_summary['FUND_REPORTED_INFO_REPORT_DATE'], format='%d-%b-%Y', errors='coerce')
                                    if not pd.isna(report_date):
                                        holding_summary['YYYYQQ'] = f"{report_date.year}Q{((report_date.month-1)//3) + 1}"
                                    else:
                                        holding_summary['YYYYQQ'] = None

                                summary.append(holding_summary)
                                if verbose and index % 10 == 0:
                                    log_safe(f"Processed {index} holdings for {zip_file}")

                    pbar.update(chunksize)

                    if debug:
                        result = chunk.apply(contains_search_term, axis=1)
                        log_safe(f"Type of result: {type(result)}")
                        log_safe(f"Result dtype: {result.dtype}")
                        log_safe(f"First few values of result:\n{result.head()}")

    except Exception as e:
        log_safe(f"Error processing {zip_file}: {str(e)}")
    
    return summary
def search_nport(search_keywords, verbose=False):
    import os
    import pandas as pd
    import tqdm
    from datetime import datetime
    import gc
    import logging

    secnport_path = os.path.join(ROOT_DIR, "SecNport")
    os.makedirs(secnport_path, exist_ok=True)
    
    # Get and sort ZIP files by date
    zip_files = [os.path.join(secnport_path, f) for f in os.listdir(secnport_path) if f.endswith('.zip')]
    zip_files = [os.path.normpath(path) for path in zip_files]
    
    def get_file_date(file):
        base_name = os.path.basename(file)
        year = base_name[:4]
        quarter_char = base_name[4]
        quarter = {'q': 1, '1': 1, 'w': 2, '2': 2, 'e': 3, '3': 3, 'r': 4, '4': 4}.get(quarter_char.lower(), None)
        if quarter is not None:
            return datetime(int(year), quarter*3 - 2, 1)
        return datetime.min  # Fallback for invalid dates
    
    zip_files.sort(key=get_file_date)
    search_terms = [term.strip() for term in search_keywords.split(',')]
    
    output_file = os.path.join(ROOT_DIR, "SecNport", f"{search_keywords.replace(',', '_')}_summary_results.csv")
    log_file = os.path.join(ROOT_DIR, "SecNport", f"{search_keywords.replace(',', '_')}_process.log")

    # Core headers from FUND_REPORTED_HOLDING and derived
    core_headers = [
        'ACCESSION_NUMBER', 'HOLDING_ID', 'FILENAME_TIMESTAMP', 'FILING_DATE',
        'ISSUER_NAME', 'ISSUER_LEI', 'ISSUER_TITLE', 'ISSUER_CUSIP', 'BALANCE',
        'UNIT', 'OTHER_UNIT_DESC', 'CURRENCY_CODE', 'CURRENCY_VALUE', 'EXCHANGE_RATE',
        'PERCENTAGE', 'PAYOFF_PROFILE', 'ASSET_CAT', 'OTHER_ASSET', 'ISSUER_TYPE',
        'OTHER_ISSUER', 'INVESTMENT_COUNTRY', 'IS_RESTRICTED_SECURITY', 'FAIR_VALUE_LEVEL',
        'DERIVATIVE_CAT', 'YYYYQQ'
    ]

    # All fields from provided schema, prefixed by TSV source
    all_tsv_fields = {
        'SUBMISSION': [
            'FILE_NUM', 'SUB_TYPE', 'IS_LAST_FILING', 'REPORT_ENDING_PERIOD', 'REPORT_DATE', 'FILING_DATE'
        ],
        'REGISTRANT': [
            'CIK', 'REGISTRANT_NAME', 'FILE_NUM', 'LEI', 'ADDRESS1', 'ADDRESS2', 'CITY', 'STATE',
            'COUNTRY', 'ZIP', 'PHONE'
        ],
        'FUND_REPORTED_INFO': [
            'SERIES_NAME', 'SERIES_ID', 'SERIES_LEI', 'TOTAL_ASSETS', 'TOTAL_LIABILITIES', 'NET_ASSETS',
            'ASSETS_ATTRBT_TO_MISC_SECURITY', 'ASSETS_INVESTED', 'BORROWING_PAY_WITHIN_1YR',
            'CTRLD_COMPANIES_PAY_WITHIN_1YR', 'OTHER_AFFILIA_PAY_WITHIN_1YR', 'OTHER_PAY_WITHIN_1YR',
            'BORROWING_PAY_AFTER_1YR', 'CTRLD_COMPANIES_PAY_AFTER_1YR', 'OTHER_AFFILIA_PAY_AFTER_1YR',
            'OTHER_PAY_AFTER_1YR', 'DELAYED_DELIVERY', 'STANDBY_COMMITMENT', 'LIQUIDATION_PREFERENCE',
            'CASH_NOT_RPTD_IN_C_OR_D', 'CREDIT_SPREAD_3MON_INVEST', 'CREDIT_SPREAD_1YR_INVEST',
            'CREDIT_SPREAD_5YR_INVEST', 'CREDIT_SPREAD_10YR_INVEST', 'CREDIT_SPREAD_30YR_INVEST',
            'CREDIT_SPREAD_3MON_NONINVEST', 'CREDIT_SPREAD_1YR_NONINVEST', 'CREDIT_SPREAD_5YR_NONINVEST',
            'CREDIT_SPREAD_10YR_NONINVEST', 'CREDIT_SPREAD_30YR_NONINVEST', 'IS_NON_CASH_COLLATERAL',
            'NET_REALIZE_GAIN_NONDERIV_MON1', 'NET_UNREALIZE_AP_NONDERIV_MON1',
            'NET_REALIZE_GAIN_NONDERIV_MON2', 'NET_UNREALIZE_AP_NONDERIV_MON2',
            'NET_REALIZE_GAIN_NONDERIV_MON3', 'NET_UNREALIZE_AP_NONDERIV_MON3',
            'SALES_FLOW_MON1', 'REINVESTMENT_FLOW_MON1', 'REDEMPTION_FLOW_MON1',
            'SALES_FLOW_MON2', 'REINVESTMENT_FLOW_MON2', 'REDEMPTION_FLOW_MON2',
            'SALES_FLOW_MON3', 'REINVESTMENT_FLOW_MON3', 'REDEMPTION_FLOW_MON3'
        ],
        'INTEREST_RATE_RISK': [
            'INTEREST_RATE_RISK_ID', 'CURRENCY_CODE', 'INTRST_RATE_CHANGE_3MON_DV01',
            'INTRST_RATE_CHANGE_1YR_DV01', 'INTRST_RATE_CHANGE_5YR_DV01', 'INTRST_RATE_CHANGE_10YR_DV01',
            'INTRST_RATE_CHANGE_30YR_DV01', 'INTRST_RATE_CHANGE_3MON_DV100', 'INTRST_RATE_CHANGE_1YR_DV100',
            'INTRST_RATE_CHANGE_5YR_DV100', 'INTRST_RATE_CHANGE_10YR_DV100', 'INTRST_RATE_CHANGE_30YR_DV100'
        ],
        'BORROWER': [
            'BORROWER_ID', 'NAME', 'LEI', 'AGGREGATE_VALUE'
        ],
        'BORROW_AGGREGATE': [
            'BORROW_AGGREGATE_ID', 'AMOUNT', 'COLLATERAL', 'INVESTMENT_CAT', 'OTHER_DESC'
        ],
        'MONTHLY_TOTAL_RETURN': [
            'MONTHLY_TOTAL_RETURN_ID', 'CLASS_ID', 'MONTHLY_TOTAL_RETURN1', 'MONTHLY_TOTAL_RETURN2',
            'MONTHLY_TOTAL_RETURN3'
        ],
        'MONTHLY_RETURN_CAT_INSTRUMENT': [
            'ASSET_CAT', 'INSTRUMENT_KIND', 'NET_REALIZED_GAIN_MON1', 'NET_UNREALIZED_AP_MON1',
            'NET_REALIZED_GAIN_MON2', 'NET_UNREALIZED_AP_MON2', 'NET_REALIZED_GAIN_MON3',
            'NET_UNREALIZED_AP_MON3'
        ],
        'IDENTIFIERS': [
            'IDENTIFIERS_ID', 'IDENTIFIER_ISIN', 'IDENTIFIER_TICKER', 'OTHER_IDENTIFIER', 'OTHER_IDENTIFIER_DESC'
        ]
    }

    # Build full headers: core + prefixed TSV fields
    headers = core_headers.copy()
    for tsv, fields in all_tsv_fields.items():
        for field in fields:
            prefixed = f"{tsv}_{field}"
            if prefixed not in headers:
                headers.append(prefixed)

    # Initialize CSV with all headers and log the action
    pd.DataFrame(columns=headers).to_csv(output_file, index=False, header=True, mode='w', encoding='utf-8')
    if verbose and log_file:
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.info(f"Initialized CSV with {len(headers)} headers: {output_file}")

    # Process ZIP files sequentially
    for zip_file in tqdm.tqdm(zip_files, desc="Files Processed", unit="file"):
        try:
            results = search_nport_swaps(zip_file, search_terms, verbose, log_file=log_file)
            if results:
                df = pd.DataFrame(results)
                df = df.reindex(columns=headers, fill_value=None)
                df.to_csv(output_file, index=False, header=False, mode='a', encoding='utf-8')
                if verbose and log_file:
                    logging.info(f"Wrote {len(df)} items to CSV for {zip_file} (total columns: {len(df.columns)})")
        except Exception as e:
            if verbose and log_file:
                logging.info(f"An error occurred while processing {zip_file}: {str(e)}")

    gc.collect()
    return output_file
def process_ncen_tsv_file(tsv_name, row, zip_file, verbose=False):
    """Process a single N-CEN TSV file for a given row and return enriched fund_summary with all fields."""
    import zipfile
    import pandas as pd
    import logging

    def log_safe(msg):
        if verbose:
            logging.info(msg)

    fund_summary = {}
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            with zip_ref.open(f'{tsv_name}.tsv') as tsvfile:
                df = pd.read_csv(tsvfile, delimiter='\t', low_memory=False)
                # Handle TSVs with ACCESSION_NUMBER (e.g., SUBMISSION, REGISTRANT)
                if tsv_name in ['SUBMISSION', 'REGISTRANT', 'REGISTRANT_WEBSITE', 'LOCATION_BOOKS_RECORD',
                                'TERMINATED_ORGANIZATION', 'DIRECTOR', 'DIRECTOR_FILE_NUMBER', 'CHIEF_COMPLIANCE_OFFICER',
                                'CCO_EMPLOYER', 'REGISTRANT_REPORTING_SERIES', 'RELEASE_NUMBER', 'PRINCIPAL_UNDERWRITER',
                                'PUBLIC_ACCOUNTANT', 'VALUATION_METHOD_CHANGE', 'VALUATION_METHOD_CHANGE_SERIES',
                                'UIT', 'SERIES_CIK', 'SPONSOR', 'TRUSTEE', 'CONTRACT_SECURITY', 'DIVESTMENT',
                                'REGISTRANT_HELDS_SECURITY', 'DEPOSITOR', 'UIT_ADMIN']:
                    match_row = df[df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']]
                    if not match_row.empty:
                        for col in match_row.columns:
                            prefixed_col = f"{tsv_name}_{col}"
                            fund_summary[prefixed_col] = match_row.iloc[0][col]
                # Handle TSVs with FUND_ID (e.g., FUND_REPORTED_INFO, SHARES_OUTSTANDING)
                elif tsv_name in ['FUND_REPORTED_INFO', 'SHARES_OUTSTANDING', 'FEEDER_FUNDS', 'MASTER_FUNDS',
                                  'FOREIGN_INVESTMENT', 'SECURITY_LENDING', 'SEC_LENDING_INDEMNITY_PROVIDER',
                                  'COLLATERAL_MANAGER', 'ADVISER', 'TRANSFER_AGENT', 'PRICING_SERVICE', 'CUSTODIAN',
                                  'SHAREHOLDER_SERVICING_AGENT', 'ADMIN', 'BROKER_DEALER', 'BROKER', 'PRINCIPAL_TRANSACTION',
                                  'LINE_OF_CREDIT_DETAIL', 'LINE_OF_CREDIT_INSTITUTION', 'CREDIT_USER',
                                  'INTER_FUND_LENDING_DETAIL', 'INTER_FUND_BORROWING_DETAIL', 'SECURITY_RELATED_ITEM',
                                  'RIGHTS_OFFERING_FUND', 'LONGTERM_DEBT_DEFAULT', 'DIVIDENDS_IN_ARREAR', 'SECURITY_EXCHANGE',
                                  'AUTHORIZED_PARTICIPANT', 'ETF']:
                    match_row = df[df['FUND_ID'] == row['FUND_ID']]
                    if not match_row.empty:
                        for col in match_row.columns:
                            prefixed_col = f"{tsv_name}_{col}"
                            fund_summary[prefixed_col] = match_row.iloc[0][col]
    except KeyError:
        if verbose:
            log_safe(f"Could not find {tsv_name} for ACCESSION_NUMBER {row['ACCESSION_NUMBER']} or FUND_ID {row.get('FUND_ID', 'N/A')} in {zip_file}")
    return fund_summary
def search_ncen_swaps(zip_file, search_terms, verbose=False, debug=False, log_file=None):
    import os
    import zipfile
    import pandas as pd
    import tqdm
    from datetime import datetime
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import logging

    summary = []
    
    # Set up logging
    if verbose and log_file:
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
    
    def log_safe(msg):
        if verbose:
            logging.info(msg)
    
    log_safe(f"Starting {zip_file}")
    
    try:
        base_name = os.path.basename(zip_file)
        year = base_name[:4]
        quarter_char = base_name[4]
        quarter = {'q': 1, '1': 1, 'w': 2, '2': 2, 'e': 3, '3': 3, 'r': 4, '4': 4}.get(quarter_char.lower(), None)

        if quarter is not None:
            quarter_start_date = datetime(int(year), quarter*3 - 2, 1)
            timestamp = int(quarter_start_date.timestamp())
        else:
            timestamp = None
            log_safe(f"Warning: Could not parse quarter from {zip_file}")
            return summary

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            if 'FUND_REPORTED_INFO.tsv' not in zip_ref.namelist():
                log_safe(f"Warning: {zip_file} does not contain FUND_REPORTED_INFO.tsv")
                return summary

            chunksize = 100000
            with zip_ref.open('FUND_REPORTED_INFO.tsv') as tsvfile:
                total_rows = sum(1 for _ in tsvfile)

            with tqdm.tqdm(total=total_rows, desc=f"Processing {zip_file}", unit="row") as pbar:
                for chunk in pd.read_csv(zip_ref.open('FUND_REPORTED_INFO.tsv'), delimiter='\t', chunksize=chunksize, low_memory=False):
                    if 'FILENAME_TIMESTAMP' not in chunk.columns:
                        chunk['FILENAME_TIMESTAMP'] = timestamp

                    string_columns = ['FUND_ID', 'FUND_NAME', 'SERIES_ID', 'LEI', 'ACCESSION_NUMBER']
                    chunk[string_columns] = chunk[string_columns].fillna('').astype(str)
                    
                    def contains_search_term(row):
                        for term in search_terms:
                            if row.astype(str).str.contains(term, case=False, regex=True, na=False).any():
                                return True
                        return False
                    
                    keyword_funds = chunk[chunk.apply(contains_search_term, axis=1)]

                    log_safe(f"Found {len(keyword_funds)} funds related to {', '.join(search_terms)} in chunk of {zip_file}")
                    
                    if not keyword_funds.empty:
                        tsv_files = [
                            'SUBMISSION', 'REGISTRANT', 'REGISTRANT_WEBSITE', 'LOCATION_BOOKS_RECORD',
                            'TERMINATED_ORGANIZATION', 'DIRECTOR', 'DIRECTOR_FILE_NUMBER', 'CHIEF_COMPLIANCE_OFFICER',
                            'CCO_EMPLOYER', 'REGISTRANT_REPORTING_SERIES', 'RELEASE_NUMBER', 'PRINCIPAL_UNDERWRITER',
                            'PUBLIC_ACCOUNTANT', 'VALUATION_METHOD_CHANGE', 'VALUATION_METHOD_CHANGE_SERIES',
                            'FUND_REPORTED_INFO', 'SHARES_OUTSTANDING', 'FEEDER_FUNDS', 'MASTER_FUNDS',
                            'FOREIGN_INVESTMENT', 'SECURITY_LENDING', 'SEC_LENDING_INDEMNITY_PROVIDER',
                            'COLLATERAL_MANAGER', 'ADVISER', 'TRANSFER_AGENT', 'PRICING_SERVICE', 'CUSTODIAN',
                            'SHAREHOLDER_SERVICING_AGENT', 'ADMIN', 'BROKER_DEALER', 'BROKER', 'PRINCIPAL_TRANSACTION',
                            'LINE_OF_CREDIT_DETAIL', 'LINE_OF_CREDIT_INSTITUTION', 'CREDIT_USER',
                            'INTER_FUND_LENDING_DETAIL', 'INTER_FUND_BORROWING_DETAIL', 'SECURITY_RELATED_ITEM',
                            'RIGHTS_OFFERING_FUND', 'LONGTERM_DEBT_DEFAULT', 'DIVIDENDS_IN_ARREAR', 'SECURITY_EXCHANGE',
                            'AUTHORIZED_PARTICIPANT', 'ETF', 'DEPOSITOR', 'UIT_ADMIN', 'UIT', 'SERIES_CIK',
                            'SPONSOR', 'TRUSTEE', 'CONTRACT_SECURITY', 'DIVESTMENT', 'REGISTRANT_HELDS_SECURITY'
                        ]
                        
                        with ProcessPoolExecutor() as executor:
                            for index, row in keyword_funds.iterrows():
                                fund_summary = {
                                    'FUND_ID': row['FUND_ID'],
                                    'FUND_NAME': row['FUND_NAME'],
                                    'SERIES_ID': row['SERIES_ID'],
                                    'FILENAME_TIMESTAMP': timestamp,
                                    'FILING_DATE': None,  # Populated from SUBMISSION.tsv
                                    'ACCESSION_NUMBER': row['ACCESSION_NUMBER'],
                                    'IS_ETF': row.get('IS_ETF', ''),
                                    'IS_ETMF': row.get('IS_ETMF', ''),
                                    'IS_INDEX': row.get('IS_INDEX', ''),
                                    'IS_FUND_OF_FUND': row.get('IS_FUND_OF_FUND', ''),
                                    'IS_MASTER_FEEDER': row.get('IS_MASTER_FEEDER', ''),
                                    'IS_MONEY_MARKET': row.get('IS_MONEY_MARKET', ''),
                                    'IS_TARGET_DATE': row.get('IS_TARGET_DATE', ''),
                                    'IS_UNDERLYING_FUND': row.get('IS_UNDERLYING_FUND', ''),
                                    'LEI': row.get('LEI', '')
                                }

                                # Parallel TSV processing
                                futures = [executor.submit(process_ncen_tsv_file, tsv_name, row, zip_file, verbose) 
                                           for tsv_name in tsv_files]
                                for future in as_completed(futures):
                                    tsv_data = future.result()
                                    fund_summary.update(tsv_data)

                                # Add quarterly data
                                if 'FUND_INFO_REPORT_DATE' in fund_summary:
                                    report_date = pd.to_datetime(fund_summary['FUND_INFO_REPORT_DATE'], errors='coerce')
                                    if not pd.isna(report_date):
                                        fund_summary['YYYYQQ'] = f"{report_date.year}Q{((report_date.month-1)//3) + 1}"
                                    else:
                                        fund_summary['YYYYQQ'] = None
                                else:
                                    fund_summary['YYYYQQ'] = None

                                summary.append(fund_summary)
                                if verbose and index % 10 == 0:
                                    log_safe(f"Processed {index} funds for {zip_file}")

                    pbar.update(chunksize)

                    if debug:
                        result = chunk.apply(contains_search_term, axis=1)
                        log_safe(f"Type of result: {type(result)}")
                        log_safe(f"Result dtype: {result.dtype}")
                        log_safe(f"First few values of result:\n{result.head()}")

    except Exception as e:
        log_safe(f"Error processing {zip_file}: {str(e)}")
    
    return summary
def search_ncen(search_keywords, verbose=False):
    import os
    import pandas as pd
    import tqdm
    from datetime import datetime
    import gc
    import logging

    secncen_path = os.path.join(ROOT_DIR, "SecNcen")
    os.makedirs(secncen_path, exist_ok=True)
    
    # Get and sort ZIP files by date
    zip_files = [os.path.join(secncen_path, f) for f in os.listdir(secncen_path) if f.endswith('.zip')]
    zip_files = [os.path.normpath(path) for path in zip_files]
    
    def get_file_date(file):
        base_name = os.path.basename(file)
        year = base_name[:4]
        quarter_char = base_name[4]
        quarter = {'q': 1, '1': 1, 'w': 2, '2': 2, 'e': 3, '3': 3, 'r': 4, '4': 4}.get(quarter_char.lower(), None)
        if quarter is not None:
            return datetime(int(year), quarter*3 - 2, 1)
        return datetime.min  # Fallback for invalid dates
    
    zip_files.sort(key=get_file_date)  # Sort files chronologically
    search_terms = [term.strip() for term in search_keywords.split(',')]
    
    output_file = os.path.join(ROOT_DIR, "SecNcen", f"{search_keywords.replace(',', '_')}_summary_results.csv")
    log_file = os.path.join(ROOT_DIR, "SecNcen", f"{search_keywords.replace(',', '_')}_process.log")

    # Core headers from FUND_REPORTED_INFO and derived
    core_headers = [
        'FUND_ID', 'FUND_NAME', 'SERIES_ID', 'FILENAME_TIMESTAMP', 'FILING_DATE', 'ACCESSION_NUMBER',
        'IS_ETF', 'IS_ETMF', 'IS_INDEX', 'IS_FUND_OF_FUND', 'IS_MASTER_FEEDER', 'IS_MONEY_MARKET',
        'IS_TARGET_DATE', 'IS_UNDERLYING_FUND', 'LEI', 'YYYYQQ'
    ]

    # All fields from N-CEN README (https://www.sec.gov/files/ncen_readme.pdf), prefixed by TSV source
    all_tsv_fields = {
        'SUBMISSION': [
            'ACCESSION_NUMBER', 'SUBMISSION_TYPE', 'CIK', 'FILING_DATE', 'REPORT_ENDING_PERIOD',
            'IS_REPORT_PERIOD_LT_12MONTH', 'FILE_NUM', 'REGISTRANT_SIGNED_NAME', 'DATE_SIGNED',
            'SIGNATURE', 'TITLE', 'IS_LEGAL_PROCEEDINGS', 'IS_PROVISION_FINANCIAL_SUPPORT',
            'IS_IPA_REPORT_INTERNAL_CONTROL', 'IS_CHANGE_ACC_PRINCIPLES', 'IS_INFO_REQUIRED_EO',
            'IS_OTHER_INFO_REQUIRED', 'IS_MATERIAL_AMENDMENTS', 'IS_INST_DEFINING_RIGHTS',
            'IS_NEW_OR_AMENDED_INV_ADV_CONT', 'IS_INFO_ITEM405', 'IS_CODE_OF_ETHICS'
        ],
        'REGISTRANT': [
            'ACCESSION_NUMBER', 'REGISTRANT_NAME', 'FILE_NUM', 'CIK', 'LEI', 'ADDRESS1', 'ADDRESS2',
            'CITY', 'STATE', 'COUNTRY', 'ZIP', 'PHONE', 'IS_FIRST_FILING', 'IS_LAST_FILING',
            'IS_FAMILY_INVESTMENT_COMPANY', 'FAMILY_INVESTMENT_COMPANY_NAME', 'INVESTMENT_COMPANY_TYPE',
            'TOTAL_SERIES', 'IS_REGISTERED_UNDER_ACT_1933', 'HAS_SECURITY_HOLDER_VOTE',
            'HAS_LEGAL_PROCEEDING', 'IS_PROCEEDING_TERMINATED', 'IS_FIDELITY_BOND_CLAIMED',
            'FIDELITY_BOND_CLAIMED_AMOUNT', 'HAS_DIRECTOR_INSURANCE_POLICY', 'HAS_DIRECTOR_FILED_CLAIM',
            'FINANCIAL_SUPPORT_2REGISTRANT', 'IS_EXEMPTIVE_ORDER', 'IS_UNDERWRITER_HIRED_OR_FIRED',
            'IS_PUB_ACCOUNTANT_CHANGED', 'IS_MATERIAL_WEAKNESS_NOTED', 'IS_ACCT_OPINION_QUALIFIED',
            'IS_VALUE_METHOD_CHANGED', 'IS_ACCT_PRINCIPLE_CHANGED', 'IS_NAV_ERROR_CORRECTED',
            'ANY_DIVIDEND_PAYMENT'
        ],
        'REGISTRANT_WEBSITE': ['ACCESSION_NUMBER', 'WEBPAGE'],
        'LOCATION_BOOKS_RECORD': [
            'ACCESSION_NUMBER', 'OFFICE_NAME', 'ADDRESS1', 'ADDRESS2', 'CITY', 'STATE', 'COUNTRY',
            'ZIP', 'PHONE', 'BOOKS_RECORDS_DESC'
        ],
        'TERMINATED_ORGANIZATION': ['ACCESSION_NUMBER', 'SERIES_NAME', 'SERIES_ID', 'TERMINATION_DATE'],
        'DIRECTOR': ['ACCESSION_NUMBER', 'DIRECTOR_SEQNUM', 'DIRECTOR_NAME', 'CRD_NUMBER', 'IS_INTERESTED_PERSON'],
        'DIRECTOR_FILE_NUMBER': ['ACCESSION_NUMBER', 'DIRECTOR_SEQNUM', 'FILE_NUMBER'],
        'CHIEF_COMPLIANCE_OFFICER': [
            'ACCESSION_NUMBER', 'CCO_SEQNUM', 'CCO_NAME', 'CRD_NUMBER', 'CCO_ADDRESS1', 'CCO_ADDRESS2',
            'CCO_CITY', 'STATE', 'COUNTRY', 'CCO_ZIP', 'IS_CHANGED_SINCE_LAST_FILING'
        ],
        'CCO_EMPLOYER': ['ACCESSION_NUMBER', 'CCO_SEQNUM', 'CCO_EMPLOYER_NAME', 'CCO_EMPLOYER_ID'],
        'REGISTRANT_REPORTING_SERIES': ['ACCESSION_NUMBER', 'SOURCE', 'SERIES_NAME', 'SERIES_ID'],
        'RELEASE_NUMBER': ['ACCESSION_NUMBER', 'RELEASE_NUMBER'],
        'PRINCIPAL_UNDERWRITER': [
            'ACCESSION_NUMBER', 'UNDERWRITER_NAME', 'FILE_NUM', 'CRD_NUM', 'UNDERWRITER_LEI',
            'STATE', 'COUNTRY', 'IS_AFFILIATED'
        ],
        'PUBLIC_ACCOUNTANT': [
            'ACCESSION_NUMBER', 'PUB_ACCOUNTANT_NAME', 'PCAOB_NUM', 'PUB_ACCOUNTANT_LEI',
            'STATE', 'COUNTRY'
        ],
        'VALUATION_METHOD_CHANGE': [
            'ACCESSION_NUMBER', 'VALUATION_METHOD_CHANGE_SEQNUM', 'DATE_OF_CHANGE', 'CHANGE_EXPLANATION',
            'ASSET_TYPE', 'ASSET_TYPE_OTHER_DESC', 'INVESTMENT_TYPE', 'STATUTORY_REGULATORY_BASIS'
        ],
        'VALUATION_METHOD_CHANGE_SERIES': [
            'ACCESSION_NUMBER', 'VALUATION_METHOD_CHANGE_SEQNUM', 'SERIES_NAME', 'SERIES_ID'
        ],
        'FUND_REPORTED_INFO': [
            'FUND_ID', 'ACCESSION_NUMBER', 'FUND_NAME', 'SERIES_ID', 'LEI', 'IS_FIRST_FILING',
            'AUTHORIZED_SHARES_CNT', 'ADDED_NEW_SHARES_CNT', 'TERMINATED_SHARES_CNT', 'IS_ETF',
            'IS_ETMF', 'IS_INDEX', 'IS_MULTI_INVERSE_INDEX', 'IS_INTERVAL', 'IS_FUND_OF_FUND',
            'IS_MASTER_FEEDER', 'IS_MONEY_MARKET', 'IS_TARGET_DATE', 'IS_UNDERLYING_FUND',
            'IS_FUND_TYPE_NA', 'IS_INDEX_AFFILIATED', 'IS_INDEX_EXCLUSIVE', 'RETURN_B4_FEES_AND_EXPENSES',
            'RETURN_AFTR_FEES_AND_EXPENSES', 'STDV_B4_FEES_AND_EXPENSES', 'STDV_AFTR_FEES_AND_EXPENSES',
            'IS_NON_DIVERSIFIED', 'IS_FOREIGN_SUBSIDIARY', 'IS_SEC_LENDING_AUTHORIZED', 'DID_LEND_SECURITIES',
            'IS_COLLATERAL_LIQUIDATED', 'IS_IMPACTED_ADVERSELY', 'IS_PYMNT_REV_SHARING_SPLIT',
            'IS_PYMNT_NON_REV_SHARING_SPLIT', 'IS_PYMNT_ADMIN_FEE', 'IS_PYMNT_CASH_COLLATERAL_FEE',
            'IS_PYMNT_INDEMNI_FEE', 'IS_PYMNT_OTHER', 'IS_PYMNT_NA', 'OTHER_FEE_DESC',
            'AVG_VALUE_SEC_LOAN', 'NET_INCOME_SEC_LENDING', 'IS_RELYON_RULE_10F_3', 'IS_RELYON_RULE_12D1_1',
            'IS_RELYON_RULE_15A_4', 'IS_RELYON_RULE_17A_6', 'IS_RELYON_RULE_17A_7', 'IS_RELYON_RULE_17A_8',
            'IS_RELYON_RULE_17E_1', 'IS_RELYON_RULE_22D_1', 'IS_RELYON_RULE_23C_1', 'IS_RELYON_RULE_32A_4',
            'IS_RELYON_RULE_6C_11', 'IS_RELYON_RULE_12D1_4', 'IS_RELYON_RULE_12D1G', 'IS_RELYON_RULE_18F_4',
            'IS_RELYON_RULE_18F_4C4', 'IS_RELYON_RULE_18F_4C2', 'IS_RELYON_RULE_18F_4DI', 'IS_RELYON_RULE_18F_4DII',
            'IS_RELYON_RULE_18F_4E', 'IS_RELYON_RULE_18F_4F', 'IS_RELYON_RULE_NA', 'HAS_EXP_LIMIT',
            'HAS_EXP_REDUCED_WAIVED', 'HAS_EXP_SUBJ_RECOUP', 'HAS_EXP_RECOUPED', 'HAS_XAGENT_HIRED_FIRED_MI',
            'HAS_PRICING_SRVC_HIRED_FIRED', 'HAS_CUSTODIAN_HIRED_FIRED_MI', 'HAS_SH_SRVC_HIRED_FIRED',
            'HAS_ADMIN_HIRED_FIRED', 'AGG_COMMISSION', 'AGG_PRINCIPAL', 'DID_PAY_BROKER_RESEARCH',
            'MONTHLY_AVG_NET_ASSETS', 'DAILY_AVG_NET_ASSETS', 'HAS_LINE_OF_CREDIT', 'HAS_INTERFUND_LENDING',
            'HAS_INTERFUND_BORROWING', 'HAS_SWING_PRICING', 'SWING_FACTOR_UPPER_LIMIT',
            'DID_MAKE_RIGHTS_OFFERING', 'DID_MAKE_SECOND_OFFERING', 'IS_SECONDARY_COMMON',
            'IS_SECONDARY_PREFERRED', 'IS_SECONDARY_WARRANTS', 'IS_SECONDARY_CONVERTIBLES',
            'IS_SECONDARY_BONDS', 'IS_SECONDARY_OTHER', 'OTHER_SECONDARY_DESC', 'DID_REPURCHASE_SECURITY',
            'IS_REPUR_COMMON', 'IS_REPUR_PREFERRED', 'IS_REPUR_WARRANTS', 'IS_REPUR_CONVERTIBLES',
            'IS_REPUR_BONDS', 'IS_REPUR_OTHER', 'OTHER_REPUR_DESC', 'IS_LONG_TERM_DEBT_DEFAULT',
            'IS_ACCUM_DIVIDEND_IN_ARREARS', 'IS_SECURITY_MAT_MODIFIED', 'MANAGEMENT_FEE',
            'NET_OPERATING_EXPENSES', 'MARKET_PRICE_PER_SHARE', 'NAV_PER_SHARE',
            'HAS_XAGENT_HIRED_FIRED_CE', 'HAS_CUSTODIAN_HIRED_FIRED_CE'
        ],
        'SHARES_OUTSTANDING': ['FUND_ID', 'CLASS_NAME', 'CLASS_ID', 'TICKER'],
        'FEEDER_FUNDS': [
            'FUND_ID', 'FUND_NAME', 'REGISTERED_FILE_NUM', 'REGISTERED_SERIES_ID',
            'REGISTERED_FUND_LEI', 'UNREGISTERED_FILE_NUM', 'UNREGISTERED_FUND_LEI'
        ],
        'MASTER_FUNDS': ['FUND_ID', 'FUND_NAME', 'FILE_NUM', 'SEC_FILE_NUM', 'FUND_LEI'],
        'FOREIGN_INVESTMENT': ['FUND_ID', 'FOREIGN_SUBSIDIARY_NAME', 'FOREIGN_SUBSIDIARY_LEI'],
        'SECURITY_LENDING': [
            'FUND_ID', 'SECURITY_LENDING_SEQNUM', 'SECURITIES_AGENT_NAME', 'SECURITIES_AGENT_LEI',
            'IS_AFFILIATED', 'SECURITY_AGENT_IDEMNITY', 'DID_INDEMNIFICATION_RIGHTS'
        ],
        'SEC_LENDING_INDEMNITY_PROVIDER': [
            'FUND_ID', 'SECURITY_LENDING_SEQNUM', 'INDEMNITY_PROVIDER_NAME', 'INDEMNITY_PROVIDER_LEI'
        ],
        'COLLATERAL_MANAGER': [
            'FUND_ID', 'COLLATERAL_MANAGER_NAME', 'COLLATERAL_MANAGER_LEI', 'IS_AFFILIATED',
            'IS_AFFILIATED_WITH_FUND'
        ],
        'ADVISER': [
            'FUND_ID', 'SOURCE', 'ADVISER_TYPE', 'ADVISER_NAME', 'FILE_NUM', 'CRD_NUM',
            'ADVISER_LEI', 'STATE', 'COUNTRY', 'IS_AFFILIATED', 'IS_ADVISOR_HIRED',
            'ADVISOR_START_DATE', 'ADVISOR_TERMINATED_DATE'
        ],
        'TRANSFER_AGENT': [
            'FUND_ID', 'SOURCE', 'TRANSFERAGENT_NAME', 'FILE_NUM', 'TRANSFERAGENT_LEI',
            'STATE', 'COUNTRY', 'IS_AFFILIATED', 'IS_SUBTRANSFER_AGENT'
        ],
        'PRICING_SERVICE': [
            'FUND_ID', 'PRICING_SERVICE_NAME', 'PRICING_SERVICE_LEI', 'OTHER_IDENTIFYING_NUM_DESC',
            'STATE', 'COUNTRY', 'IS_AFFILIATED'
        ],
        'CUSTODIAN': [
            'FUND_ID', 'SOURCE', 'CUSTODIAN_NAME', 'CUSTODIAN_LEI', 'STATE', 'COUNTRY',
            'IS_AFFILIATED', 'IS_SUB_CUSTODIAN', 'CUSTODY_TYPE', 'OTHER_CUSTODIAN_DESC'
        ],
        'SHAREHOLDER_SERVICING_AGENT': [
            'FUND_ID', 'AGENT_NAME', 'AGENT_LEI', 'OTHER_IDENTIFYING_NUM_DESC', 'STATE',
            'COUNTRY', 'IS_AFFILIATED', 'IS_SUBSHARE'
        ],
        'ADMIN': [
            'FUND_ID', 'ADMIN_NAME', 'ADMIN_LEI', 'OTHER_IDENTIFYING_NUM', 'STATE',
            'COUNTRY', 'IS_AFFILIATED', 'IS_SUB_ADMIN'
        ],
        'BROKER_DEALER': [
            'FUND_ID', 'BROKER_DEALER_NAME', 'FILE_NUM', 'CRD_NUM', 'BROKER_DEALER_LEI',
            'STATE', 'COUNTRY', 'COMMISSION'
        ],
        'BROKER': [
            'FUND_ID', 'BROKER_NAME', 'FILE_NUM', 'CRD_NUM', 'BROKER_LEI', 'STATE',
            'COUNTRY', 'GROSS_COMMISSION'
        ],
        'PRINCIPAL_TRANSACTION': [
            'FUND_ID', 'PRINCIPAL_NAME', 'FILE_NUM', 'CRD_NUM', 'PRINCIPAL_LEI', 'STATE',
            'COUNTRY', 'PRINCIPAL_TOTAL_PURCHASE_SALE'
        ],
        'LINE_OF_CREDIT_DETAIL': [
            'FUND_ID', 'LINE_OF_CREDIT_SEQNUM', 'IS_CREDIT_LINE_COMMITTED', 'LINE_OF_CREDIT_SIZE',
            'CREDIT_TYPE', 'IS_CREDIT_LINE_USED', 'AVERAGE_CREDIT_LINE_USED', 'DAYS_CREDIT_USED'
        ],
        'LINE_OF_CREDIT_INSTITUTION': ['FUND_ID', 'LINE_OF_CREDIT_SEQNUM', 'CREDIT_INSTITUTION_NAME'],
        'CREDIT_USER': ['FUND_ID', 'LINE_OF_CREDIT_SEQNUM', 'FUND_NAME', 'SEC_FILE_NUM'],
        'INTER_FUND_LENDING_DETAIL': ['FUND_ID', 'LENDING_LOAN_AVERAGE', 'LENDING_DAYS_OUTSTANDING'],
        'INTER_FUND_BORROWING_DETAIL': ['FUND_ID', 'BORROWING_LOAN_AVERAGE', 'BORROWING_DAYS_OUTSTANDING'],
        'SECURITY_RELATED_ITEM': [
            'FUND_ID', 'SECURITY_RELATED_ITEM_SEQNUM', 'DESCRIPTION', 'SECURITY_CLASS_TITLE',
            'OTHER_SECURITY_DESCRIPTION', 'EXCHANGE', 'TICKER_SYMBOL'
        ],
        'RIGHTS_OFFERING_FUND': [
            'FUND_ID', 'IS_RIGHTS_OFFER_COMMON', 'IS_RIGHTS_OFFER_PREFERRED', 'IS_RIGHTS_OFFER_WARRANTS',
            'IS_RIGHTS_OFFER_CONVERTIBLES', 'IS_RIGHTS_OFFER_BONDS', 'IS_RIGHTS_OFFER_OTHER',
            'RIGHTS_OFFER_DESC', 'PCT_PARTCI_PRIMARY_OFFERING'
        ],
        'LONGTERM_DEBT_DEFAULT': [
            'FUND_ID', 'DEFAULT_NATURE', 'DEFAULT_DATE', 'DEFAULT_AMNT_PER_1000', 'TOTAL_DEFAULT_AMNT'
        ],
        'DIVIDENDS_IN_ARREAR': ['FUND_ID', 'ISSUE_TITLE', 'AMOUNT_PER_SHARE_IN_ARREAR'],
        'SECURITY_EXCHANGE': ['FUND_ID', 'FUND_EXCHANGE', 'FUND_TICKER_SYMBOL'],
        'AUTHORIZED_PARTICIPANT': [
            'FUND_ID', 'PARTICIPANT_NAME', 'FILE_NUM', 'CRD_NUM', 'PARTICIPANT_LEI',
            'PURCHASE_VALUE', 'REDEEM_VALUE'
        ],
        'ETF': [
            'FUND_ID', 'FUND_NAME', 'SERIES_ID', 'IS_COLLATERAL_REQUIRED', 'NUM_SHARES_PER_CREATION_UNIT',
            'PURCHASED_AVG_PCT_CASH', 'PURCHASED_STDV_PCT_CASH', 'PURCHASED_AVG_PCT_NON_CASH',
            'PURCHASED_STDV_PCT_NON_CASH', 'REDEEMED_AVG_PCT_CASH', 'REDEEMED_STDV_PCT_CASH',
            'REDEEMED_AVG_PCT_NON_CASH', 'REDEEMED_STDV_PCT_NON_CASH', 'PURCH_AVG_FEE_PER_UNIT',
            'PURCH_AVG_FEE_SAME_DAY', 'PURCH_AVG_FEE_PERCENTAGE', 'PURCH_AVG_FEE_CASH_PER_UNIT',
            'PURCH_AVG_FEE_CASH_SAME_DAY', 'PURCH_AVG_FEE_CASH_PERCENTAGE', 'REDEEM_AVG_FEE_PER_UNIT',
            'REDEEM_AVG_FEE_SAME_DAY', 'REDEEM_AVG_FEE_PERCENTAGE', 'REDEEM_AVG_FEE_CASH_PER_UNIT',
            'REDEEM_AVG_FEE_CASH_SAME_DAY', 'REDEEM_AVG_FEE_CASH_PERCENTAGE',
            'IS_PERF_TRACKED_AFFILIA_PERSON', 'IS_PERF_TRACKED_EXCLUSIVELY',
            'ANNUAL_DIFF_B4_FEE_EXPENSE', 'ANNUAL_DIFF_AFTER_FEE_EXPENSE',
            'ANNUAL_STDV_B4_FEE_EXPENSE', 'ANNUAL_STDV_AFTER_FEE_EXPENSE', 'IS_FUND_IN_KIND_ETF'
        ],
        'DEPOSITOR': [
            'ACCESSION_NUMBER', 'DEPOSITOR_NAME', 'CRD_NUM', 'DEPOSITOR_LEI', 'STATE',
            'COUNTRY', 'ULTIMATE_PARENT_NAME'
        ],
        'UIT_ADMIN': [
            'ACCESSION_NUMBER', 'UIT_ADMIN_NAME', 'UIT_ADMIN_LEI', 'OTHER_IDENTIFYING_NUM',
            'STATE', 'COUNTRY', 'IS_AFFILIATED', 'IS_SUB_ADMIN'
        ],
        'UIT': [
            'ACCESSION_NUMBER', 'IS_ADMIN_HIRED_FIRED', 'IS_SEPERATE_ACCT', 'EXISTING_SERIES_CNT',
            'NEW_SERIES_CNT', 'NEW_SERIES_AGG_VALUE', 'SERIES_CURRENT_PROSPECTUS',
            'SERIES_CNT_ADDITIONAL_UNITS', 'TOTAL_VALUE_ADDITIONAL_UNIT', 'VALUE_UNIT_PLACED_SUBSEQUENT',
            'TOTAL_ASSET_FOR_ALL_SERIES', 'SERIES_ID', 'NUM_CONTRACTS', 'IS_RELYON_RULE_6C_7',
            'IS_RELYON_RULE_11A_2', 'IS_RELYON_RULE_12D1_4', 'IS_RELYON_RULE_12D1G'
        ],
        'SERIES_CIK': ['ACCESSION_NUMBER', 'SERIES_CIK'],
        'SPONSOR': ['ACCESSION_NUMBER', 'SPONSOR_NAME', 'CRD_NUM', 'SPONSOR_LEI', 'STATE', 'COUNTRY'],
        'TRUSTEE': ['ACCESSION_NUMBER', 'TRUSTEE_NAME', 'STATE', 'COUNTRY'],
        'CONTRACT_SECURITY': [
            'ACCESSION_NUMBER', 'SECURITY_NAME', 'CONTRACT_ID', 'TOTAL_ASSET', 'NUM_CONTRACT_SOLD',
            'GROSS_PREMIUM_RECEIVED', 'GROSS_PREMIUM_RECEIVED_SEC1035', 'NUM_CONTRACT_AFFECTED_PAID',
            'CONTRACT_VALUE_REDEEMED', 'CONTRAC_VALUE_REDEEMED_SEC1035', 'NUM_CONTRACT_AFFECTED_REDEEMED'
        ],
        'DIVESTMENT': [
            'ACCESSION_NUMBER', 'ISSUER_NAME', 'TICKER', 'CUSIP', 'DIVESTED_NUM_SHARES',
            'DIVESTED_DATE', 'STATUTE_NAME'
        ],
        'REGISTRANT_HELDS_SECURITY': ['ACCESSION_NUMBER', 'TICKER', 'CUSIP', 'TOTAL_NUM_SHARES']
    }

    # Build full headers: core + prefixed TSV fields
    headers = core_headers.copy()
    for tsv, fields in all_tsv_fields.items():
        for field in fields:
            prefixed = f"{tsv}_{field}"
            if prefixed not in headers:  # Avoid duplicates
                headers.append(prefixed)

    # Initialize CSV with all headers and log the action
    pd.DataFrame(columns=headers).to_csv(output_file, index=False, header=True, mode='w', encoding='utf-8')
    if verbose and log_file:
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.info(f"Initialized CSV with {len(headers)} headers: {output_file}")

    # Process ZIP files sequentially
    for zip_file in tqdm.tqdm(zip_files, desc="Files Processed", unit="file"):
        try:
            results = search_ncen_swaps(zip_file, search_terms, verbose, log_file=log_file)
            if results:
                df = pd.DataFrame(results)
                # Ensure DataFrame columns match all headers order
                df = df.reindex(columns=headers, fill_value=None)
                df.to_csv(output_file, index=False, header=False, mode='a', encoding='utf-8')
                if verbose and log_file:
                    logging.info(f"Wrote {len(df)} items to CSV for {zip_file} (total columns: {len(df.columns)})")
        except Exception as e:
            if verbose and log_file:
                logging.info(f"An error occurred while processing {zip_file}: {str(e)}")

    gc.collect()
    return output_file
def process_nmfp_tsv_file(tsv_name, row, zip_file, verbose=False):
    import zipfile
    import pandas as pd
    import logging

    def log_safe(msg):
        if verbose:
            logging.info(msg)

    holding_summary = {}
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            tsv_filename = f"NMFP_{tsv_name}.tsv"
            if tsv_filename not in zip_ref.namelist():
                log_safe(f"Warning: {tsv_filename} not found in {zip_file}")
                return holding_summary
            with zip_ref.open(tsv_filename) as tsvfile:
                df = pd.read_csv(tsvfile, delimiter='\t', low_memory=False)
                # Handle TSVs with ACCESSION_NUMBER
                if tsv_name in ['SUBMISSION', 'FUND', 'SERIESLEVELINFO', 'MASTERFEEDERFUND', 'ADVISER', 'ADMINISTRATOR', 'TRANSFERAGENT',
                                'SERIESSHADOWPRICE_L', 'CLASSLEVELINFO', 'NETASSETVALUEPERSHARE_L', 'LIQUIDASSETSDETAILS',
                                'SEVENDAYGROSSYIELD', 'DLYNETASSETVALUEPERSHARS']:
                    match_row = df[df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']]
                    if not match_row.empty:
                        for col in match_row.columns:
                            prefixed_col = f"{tsv_name}_{col}"
                            holding_summary[prefixed_col] = match_row.iloc[0][col]
                        log_safe(f"Matched {tsv_name} for ACCESSION_NUMBER {row['ACCESSION_NUMBER']}")
                    else:
                        log_safe(f"No match for {tsv_name} with ACCESSION_NUMBER {row['ACCESSION_NUMBER']}")
                # Handle TSVs with SECURITY_ID
                elif tsv_name in ['SCHPORTFOLIOSECURITIES', 'COLLATERALISSUERS', 'NRSRO', 'DEMANDFEATURE', 'GUARANTOR', 'ENHANCEMENTPROVIDER']:
                    match_row = df[df['SECURITY_ID'] == row['SECURITY_ID']]
                    if not match_row.empty:
                        for col in match_row.columns:
                            prefixed_col = f"{tsv_name}_{col}"
                            holding_summary[prefixed_col] = match_row.iloc[0][col]
                        log_safe(f"Matched {tsv_name} for SECURITY_ID {row['SECURITY_ID']}")
                    else:
                        log_safe(f"No match for {tsv_name} with SECURITY_ID {row['SECURITY_ID']}")
    except Exception as e:
        log_safe(f"Error processing {tsv_filename} in {zip_file}: {str(e)}")
    return holding_summary
def search_nmfp_swaps(zip_file, search_terms, verbose=False, debug=False, log_file="SecNmfp/repo_process.log"):
    import os
    import zipfile
    import pandas as pd
    import tqdm
    from datetime import datetime
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import logging

    # Set up logging with default file
    if verbose and log_file:
        log_dir = os.path.dirname(log_file) or '.'
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', filemode='a')
    
    summary = []
    
    def log_safe(msg):
        if verbose:
            logging.info(msg)
    
    log_safe(f"Starting {zip_file}")
    
    try:
        base_name = os.path.basename(zip_file)
        year = base_name[:4]
        quarter_char = base_name[4]
        quarter = {'q': 1, '1': 1, 'w': 2, '2': 2, 'e': 3, '3': 3, 'r': 4, '4': 4}.get(quarter_char.lower(), None)

        if quarter is not None:
            quarter_start_date = datetime(int(year), quarter*3 - 2, 1)
            timestamp = int(quarter_start_date.timestamp())
        else:
            timestamp = None
            log_safe(f"Warning: Could not parse quarter from {zip_file}")
            return summary

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            if 'NMFP_SCHPORTFOLIOSECURITIES.tsv' not in zip_ref.namelist():
                log_safe(f"Warning: {zip_file} does not contain NMFP_SCHPORTFOLIOSECURITIES.tsv")
                return summary

            chunksize = 100000
            with zip_ref.open('NMFP_SCHPORTFOLIOSECURITIES.tsv') as tsvfile:
                total_rows = sum(1 for _ in tsvfile)
                tsvfile.seek(0)  # Reset file pointer after counting

            with tqdm.tqdm(total=total_rows, desc=f"Processing {zip_file}", unit="row") as pbar:
                for chunk in pd.read_csv(zip_ref.open('NMFP_SCHPORTFOLIOSECURITIES.tsv'), delimiter='\t', chunksize=chunksize,
                                       low_memory=False, encoding='utf-8', on_bad_lines='skip'):
                    if 'FILENAME_TIMESTAMP' not in chunk.columns:
                        chunk['FILENAME_TIMESTAMP'] = timestamp

                    string_columns = ['NAMEOFISSUER', 'TITLEOFISSUER', 'BRIEFDESCRIPTION', 'ACCESSION_NUMBER', 'SECURITY_ID', 'CUSIP_NUMBER']
                    log_safe(f"Chunk columns: {chunk.columns.tolist()}")
                    log_safe(f"Sample NAMEOFISSUER: {chunk['NAMEOFISSUER'].head().tolist() if 'NAMEOFISSUER' in chunk.columns else 'Column missing'}")
                    chunk[string_columns] = chunk[string_columns].fillna('').astype(str)
                    
                    def contains_search_term(row):
                        for term in search_terms:
                            for col in string_columns:
                                if pd.notna(row[col]) and term.lower() in str(row[col]).lower():
                                    return True
                        return False
                    
                    keyword_securities = chunk[chunk.apply(contains_search_term, axis=1)]
                    log_safe(f"Processed chunk with {len(chunk)} rows, found {len(keyword_securities)} matches for {', '.join(search_terms)} in {zip_file}")

                    if not keyword_securities.empty:
                        tsv_files = [
                            'SUBMISSION', 'FUND', 'SERIESLEVELINFO', 'MASTERFEEDERFUND', 'ADVISER', 'ADMINISTRATOR', 'TRANSFERAGENT',
                            'SERIESSHADOWPRICE_L', 'CLASSLEVELINFO', 'NETASSETVALUEPERSHARE_L', 'LIQUIDASSETSDETAILS',
                            'SEVENDAYGROSSYIELD', 'DLYNETASSETVALUEPERSHARS', 'SCHPORTFOLIOSECURITIES', 'COLLATERALISSUERS',
                            'NRSRO', 'DEMANDFEATURE', 'GUARANTOR', 'ENHANCEMENTPROVIDER'
                        ]
                        
                        with ProcessPoolExecutor() as executor:
                            for index, row in keyword_securities.iterrows():
                                holding_summary = {
                                    'ACCESSION_NUMBER': row['ACCESSION_NUMBER'],
                                    'SECURITY_ID': row['SECURITY_ID'],
                                    'FILENAME_TIMESTAMP': timestamp,
                                    'FILING_DATE': None,
                                    'NAMEOFISSUER': row['NAMEOFISSUER'] if 'NAMEOFISSUER' in row else None,
                                    'TITLEOFISSUER': row['TITLEOFISSUER'] if 'TITLEOFISSUER' in row else None,
                                    'CUSIP_NUMBER': row['CUSIP_NUMBER'] if 'CUSIP_NUMBER' in row else None,
                                    'LEI': row['LEI'] if 'LEI' in row else None,
                                    'ISIN': row['ISIN'] if 'ISIN' in row else None,
                                    'CIK': row['CIK'] if 'CIK' in row else None,
                                    'INVESTMENTCATEGORY': row['INVESTMENTCATEGORY'] if 'INVESTMENTCATEGORY' in row else None,
                                    'BRIEFDESCRIPTION': row['BRIEFDESCRIPTION'] if 'BRIEFDESCRIPTION' in row else None,
                                    'REPURCHASEAGREEMENTOPENFLAG': row['REPURCHASEAGREEMENTOPENFLAG'] if 'REPURCHASEAGREEMENTOPENFLAG' in row else None,
                                    'INVESTMENTMATURITYDATEWAM': row['INVESTMENTMATURITYDATEWAM'] if 'INVESTMENTMATURITYDATEWAM' in row else None,
                                    'YIELDOFTHESECURITYASOFREPORTIN': row['YIELDOFTHESECURITYASOFREPORTIN'] if 'YIELDOFTHESECURITYASOFREPORTIN' in row else None,
                                    'INCLUDINGVALUEOFANYSPONSORSUPP': row['INCLUDINGVALUEOFANYSPONSORSUPP'] if 'INCLUDINGVALUEOFANYSPONSORSUPP' in row else None,
                                    'EXCLUDINGVALUEOFANYSPONSORSUPP': row['EXCLUDINGVALUEOFANYSPONSORSUPP'] if 'EXCLUDINGVALUEOFANYSPONSORSUPP' in row else None,
                                    'PERCENTAGEOFMONEYMARKETFUNDNET': row['PERCENTAGEOFMONEYMARKETFUNDNET'] if 'PERCENTAGEOFMONEYMARKETFUNDNET' in row else None,
                                    'DAILYLIQUIDASSETSECURITYFLAG': row['DAILYLIQUIDASSETSECURITYFLAG'] if 'DAILYLIQUIDASSETSECURITYFLAG' in row else None,
                                    'WEEKLYLIQUIDASSETSECURITYFLAG': row['WEEKLYLIQUIDASSETSECURITYFLAG'] if 'WEEKLYLIQUIDASSETSECURITYFLAG' in row else None,
                                    'YYYYQQ': None
                                }

                                futures = [executor.submit(process_nmfp_tsv_file, tsv_name, row, zip_file, verbose) 
                                          for tsv_name in tsv_files]
                                for future in as_completed(futures):
                                    tsv_data = future.result()
                                    holding_summary.update(tsv_data)

                                if 'SUBMISSION_REPORT_ENDING_PERIOD' in holding_summary:
                                    report_date = pd.to_datetime(holding_summary['SUBMISSION_REPORT_ENDING_PERIOD'], errors='coerce')
                                    if not pd.isna(report_date):
                                        holding_summary['YYYYQQ'] = f"{report_date.year}Q{((report_date.month-1)//3) + 1}"
                                    else:
                                        holding_summary['YYYYQQ'] = None
                                else:
                                    holding_summary['YYYYQQ'] = None

                                summary.append(holding_summary)
                                if verbose and index % 10 == 0:
                                    log_safe(f"Processed {index} securities for {zip_file}")

                    pbar.update(chunksize)

    except Exception as e:
        log_safe(f"Error processing {zip_file}: {str(e)}")
    
    log_safe(f"Returning {len(summary)} results for {zip_file}")
    return summary
def search_nmfp(search_keywords, verbose=False):
    import os
    import pandas as pd
    import tqdm
    from datetime import datetime
    import gc
    import logging

    secnmfp_path = os.path.join(ROOT_DIR, "SecNmfp")
    os.makedirs(secnmfp_path, exist_ok=True)
    
    # Get and sort ZIP files by date
    zip_files = [os.path.join(secnmfp_path, f) for f in os.listdir(secnmfp_path) if f.endswith('.zip')]
    zip_files = [os.path.normpath(path) for path in zip_files]
    def log_safe(msg):
        if verbose:
            logging.info(msg)
    def get_file_date(file):
        base_name = os.path.basename(file)
        year = base_name[:4]
        quarter_char = base_name[4]
        quarter = {'q': 1, '1': 1, 'w': 2, '2': 2, 'e': 3, '3': 3, 'r': 4, '4': 4}.get(quarter_char.lower(), None)
        if quarter is not None:
            return datetime(int(year), quarter*3 - 2, 1)
        return datetime.min  # Fallback for invalid dates
    
    zip_files.sort(key=get_file_date)  # Sort files chronologically
    search_terms = [term.strip() for term in search_keywords.split(',')]
    
    output_file = os.path.join(ROOT_DIR, "SecNmfp", f"{search_keywords.replace(',', '_')}_summary_results.csv")
    log_file = os.path.join(ROOT_DIR, "SecNmfp", f"{search_keywords.replace(',', '_')}_process.log")

    # Core headers from SCHPORTFOLIOSECURITIES and derived
    core_headers = [
        'ACCESSION_NUMBER', 'SECURITY_ID', 'FILENAME_TIMESTAMP', 'FILING_DATE', 'ISSUER_NAME',
        'SECURITY_DESCRIPTION', 'CUSIP', 'TICKER', 'VALUE', 'AMOUNT', 'CURRENCY', 'MATURITY_DATE',
        'IS_DAILY_LIQUID', 'IS_WEEKLY_LIQUID', 'IS_REDEEMABLE', 'IS_REPURCHASE_AGREEMENT',
        'RATE', 'PORTFOLIO_PERCENTAGE', 'FAIR_VALUE', 'CATEGORY', 'COUNTRY', 'INDUSTRY',
        'RATING', 'IS_DERIVATIVE', 'DERIVATIVE_TYPE', 'YYYYQQ'
    ]

    # All fields from NMFP README
    all_tsv_fields = {
        'SUBMISSION': [
            'ACCESSION_NUMBER', 'FILING_DATE', 'REPORT_ENDING_PERIOD', 'IS_LAST_FILING', 'SUB_TYPE'
        ],
        'FUND': [
            'ACCESSION_NUMBER', 'FILENUMBER', 'SERIESID', 'FUND_TYPE', 'SUCCESSOR_FUND_NAME',
            'SUCCESSOR_FUND_LEI', 'ACQUIRED_FUND_NAME', 'ACQUIRED_FUND_LEI'
        ],
        'SERIESLEVELINFO': [
            'ACCESSION_NUMBER', 'SERIESID', 'FUND_NAME', 'FUND_LEI', 'FUND_ADDRESS1', 'FUND_ADDRESS2',
            'FUND_CITY', 'FUND_STATE', 'FUND_COUNTRY', 'FUND_ZIP', 'FUND_PHONE', 'IS_MONEY_MARKET',
            'IS_GOVERNMENT', 'IS_PRIME', 'IS_TAX_EXEMPT', 'IS_RETAIL', 'IS_INSTITUTIONAL',
            'IS_STABLE_NAV', 'IS_STABLE_VALUE', 'IS_MASTER_FEEDER', 'IS_FEEDER', 'IS_ETF',
            'TOTAL_ASSETS', 'TOTAL_LIABILITIES', 'NET_ASSETS', 'WAM', 'WAL', 'DAILY_LIQUID_ASSETS',
            'WEEKLY_LIQUID_ASSETS', 'SHARES_OUTSTANDING', 'NAV_PER_SHARE', 'SEVEN_DAY_LIQUIDITY',
            'SEVEN_DAY_YIELD', 'WEEKLY_GROSS_YIELD', 'REPORT_DATE'
        ],
        'MASTERFEEDERFUND': [
            'ACCESSION_NUMBER', 'SERIESID', 'FUND_TYPE', 'MASTER_FUND_NAME', 'MASTER_FUND_LEI',
            'MASTER_FUND_FILE_NUMBER', 'MASTER_FUND_SERIES_ID'
        ],
        'ADVISER': [
            'ACCESSION_NUMBER', 'ADVISORFILENUMBER', 'ADVISER_TYPE', 'ADVISER_NAME', 'ADVISER_LEI',
            'ADVISER_ADDRESS1', 'ADVISER_ADDRESS2', 'ADVISER_CITY', 'ADVISER_STATE', 'ADVISER_COUNTRY',
            'ADVISER_ZIP', 'ADVISER_PHONE'
        ],
        'ADMINISTRATOR': [
            'ACCESSION_NUMBER', 'ADMINISTRATORNAME', 'ADMINISTRATOR_LEI', 'ADMINISTRATOR_ADDRESS1',
            'ADMINISTRATOR_ADDRESS2', 'ADMINISTRATOR_CITY', 'ADMINISTRATOR_STATE', 'ADMINISTRATOR_COUNTRY',
            'ADMINISTRATOR_ZIP', 'ADMINISTRATOR_PHONE'
        ],
        'TRANSFERAGENT': [
            'ACCESSION_NUMBER', 'FILENUMBER', 'TRANSFERAGENT_NAME', 'TRANSFERAGENT_LEI',
            'TRANSFERAGENT_ADDRESS1', 'TRANSFERAGENT_ADDRESS2', 'TRANSFERAGENT_CITY',
            'TRANSFERAGENT_STATE', 'TRANSFERAGENT_COUNTRY', 'TRANSFERAGENT_ZIP', 'TRANSFERAGENT_PHONE'
        ],
        'SERIESSHADOWPRICE_L': [
            'ACCESSION_NUMBER', 'SHADOW_PRICE_DATE', 'SHADOW_NAV', 'MARKET_BASED_NAV'
        ],
        'CLASSLEVELINFO': [
            'ACCESSION_NUMBER', 'CLASSESID', 'CLASS_NAME', 'CLASS_LEI', 'SHARES_OUTSTANDING',
            'NAV_PER_SHARE', 'IS_STABLE_NAV', 'IS_STABLE_VALUE'
        ],
        'NETASSETVALUEPERSHARE_L': [
            'ACCESSION_NUMBER', 'CLASSESID', 'TYPE', 'NAV_DATE', 'NAV_PER_SHARE'
        ],
        'SCHPORTFOLIOSECURITIES': [
            'ACCESSION_NUMBER', 'SECURITY_ID', 'ISSUER_NAME', 'SECURITY_DESCRIPTION', 'CUSIP',
            'TICKER', 'VALUE', 'AMOUNT', 'CURRENCY', 'MATURITY_DATE', 'IS_DAILY_LIQUID',
            'IS_WEEKLY_LIQUID', 'IS_REDEEMABLE', 'IS_REPURCHASE_AGREEMENT', 'RATE',
            'PORTFOLIO_PERCENTAGE', 'FAIR_VALUE', 'CATEGORY', 'COUNTRY', 'INDUSTRY',
            'RATING', 'IS_DERIVATIVE', 'DERIVATIVE_TYPE', 'AMORTIZED_COST', 'PRINCIPAL_AMOUNT',
            'YIELD_TO_MATURITY', 'EFFECTIVE_MATURITY', 'MAXIMUM_MATURITY', 'IS_GUARANTEED'
        ],
        'COLLATERALISSUERS': [
            'ACCESSION_NUMBER', 'SECURITY_ID', 'NAMEOFCOLLATERALISSUER', 'COLLATERALMATURITYDATE',
            'VALUEOFCOLLATERALTOTHENEARESTC'
        ],
        'NRSRO': [
            'ACCESSION_NUMBER', 'SECURITY_ID', 'IDENTITY', 'TYPE', 'NAMEOFNRSRO', 'RATING'
        ],
        'DEMANDFEATURE': [
            'ACCESSION_NUMBER', 'SECURITY_ID', 'IDENTITYOFDEMANDFEATUREISSUER', 'DEMAND_FEATURE_TYPE'
        ],
        'GUARANTOR': [
            'ACCESSION_NUMBER', 'SECURITY_ID', 'IDENTITYOFTHEGUARANTOR', 'GUARANTOR_TYPE'
        ],
        'ENHANCEMENTPROVIDER': [
            'ACCESSION_NUMBER', 'SECURITY_ID', 'IDENTITYOFENHANCEMENTPROVIDER', 'TYPEOFENHANCEMENT'
        ],
        'LIQUIDASSETSDETAILS': [
            'ACCESSION_NUMBER', 'TOTLIQUIDASSETSNEARPCTDATE', 'DAILY_LIQUID_ASSETS', 'WEEKLY_LIQUID_ASSETS',
            'TOTAL_ASSETS', 'DAILY_LIQUID_PERCENTAGE', 'WEEKLY_LIQUID_PERCENTAGE'
        ],
        'SEVENDAYGROSSYIELD': [
            'ACCESSION_NUMBER', 'SEVENDAYGROSSYIELDDATE', 'SEVEN_DAY_GROSS_YIELD'
        ],
        'DLYNETASSETVALUEPERSHARS': [
            'ACCESSION_NUMBER', 'NAV_DATE', 'NAV_PER_SHARE'
        ]
    }

    # Build full headers
    headers = core_headers.copy()
    for tsv, fields in all_tsv_fields.items():
        for field in fields:
            prefixed = f"{tsv}_{field}"
            if prefixed not in headers:
                headers.append(prefixed)

    # Initialize CSV with all headers
    pd.DataFrame(columns=headers).to_csv(output_file, index=False, header=True, mode='w', encoding='utf-8')
    if verbose and log_file:
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.info(f"Initialized CSV with {len(headers)} headers: {output_file}")

    # Process ZIP files sequentially
    for zip_file in tqdm.tqdm(zip_files, desc="Files Processed", unit="file"):
        try:
            results = search_nmfp_swaps(zip_file, search_terms, verbose, log_file=log_file)
            if results:
                log_safe(f"Appending {len(results)} rows for {zip_file}")
                df = pd.DataFrame(results)
                df = df.reindex(columns=headers, fill_value=None)
                df.to_csv(output_file, index=False, header=False, mode='a', encoding='utf-8')
                logging.info(f"Wrote {len(df)} rows to CSV for {zip_file} (total columns: {len(df.columns)})")
            else:
                logging.info(f"No results for {zip_file}")
        except Exception as e:
            logging.info(f"An error occurred while processing {zip_file}: {str(e)}")

    gc.collect()
    return output_file
def main_search(zip_file, search_keyword, verbose=False, looking_for_swaps=False):
    import tqdm, pandas as pd
    if verbose:
        print(f"Starting {zip_file}")
    summary = []
    
    try:
        base_name = os.path.basename(zip_file)
        year = base_name[:4]
        quarter_char = base_name[4]
        quarter = {
            'q': 1, '1': 1,
            'w': 2, '2': 2,
            'e': 3, '3': 3,
            'r': 4, '4': 4
        }.get(quarter_char.lower(), None)

        if quarter is not None:
            quarter_start_date = datetime(int(year), quarter*3 - 2, 1)
            timestamp = int(quarter_start_date.timestamp())
        else:
            timestamp = None

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            if 'FUND_REPORTED_HOLDING.tsv' not in zip_ref.namelist():
                if verbose:
                    print(f"Warning: {zip_file} does not contain FUND_REPORTED_HOLDING.tsv")
                return summary

            chunksize = 100000  # Adjust based on memory usage
            total_rows = 0  # Estimate total rows, this might need adjustment based on file size
            with zip_ref.open('FUND_REPORTED_HOLDING.tsv') as tsvfile:
                total_rows = sum(1 for _ in tsvfile)  # Count lines for progress estimation

            with tqdm.tqdm(total=total_rows, desc=f"Processing {zip_file}", unit="row") as pbar:
                for chunk in pd.read_csv(zip_ref.open('FUND_REPORTED_HOLDING.tsv'), delimiter='\t', chunksize=chunksize, low_memory=False):

                    # Ensure 'FILENAME_TIMESTAMP' column exists, using timestamp from filename
                    if 'FILENAME_TIMESTAMP' not in chunk.columns:
                        chunk['FILENAME_TIMESTAMP'] = f"{year}{quarter_char}"  # Add column with the year and quarter from the filename

                    # Ensure all columns are treated as strings for string operations
                    string_columns = ['ISSUER_NAME', 'ISSUER_TITLE', 'ACCESSION_NUMBER', 'HOLDING_ID', 'FILENAME_TIMESTAMP',
                                    'ISSUER_LEI', 'ISSUER_CUSIP', 'BALANCE', 'UNIT', 'OTHER_UNIT_DESC', 'CURRENCY_CODE',
                                    'CURRENCY_VALUE', 'EXCHANGE_RATE', 'PERCENTAGE', 'PAYOFF_PROFILE', 'ASSET_CAT',
                                    'OTHER_ASSET', 'ISSUER_TYPE', 'OTHER_ISSUER', 'INVESTMENT_COUNTRY',
                                    'IS_RESTRICTED_SECURITY', 'FAIR_VALUE_LEVEL', 'DERIVATIVE_CAT']
                    chunk[string_columns] = chunk[string_columns].fillna('').astype(str)
                    pbar.update(len(chunk))

                    if search_keyword == 'SWAPS$':
                        # Special case for SWAPS$ to search across all columns
                        return search_nport_swaps(zip_file, verbose, debug=True)
                    else:
                        # Escape special regex characters in each search term
                        search_terms = [re.escape(term.strip()) for term in search_keyword.split(',')]
                        
                        conditions = []
                        for term in search_terms:
                            condition = False
                            for column in string_columns:
                                if column in chunk.columns:
                                    condition = condition | chunk[column].str.contains(term, case=False, na=False, regex=True)
                            conditions.append(condition)
                        
                        if conditions:
                            keyword_holdings = chunk[pd.concat(conditions, axis=1).any(axis=1)]
                        else:
                            keyword_holdings = pd.DataFrame(columns=chunk.columns)  # Empty DataFrame with same columns
                        
                        if looking_for_swaps:
                            keyword_holdings = keyword_holdings[keyword_holdings['DERIVATIVE_CAT'].str.contains('swap', case=False, na=False, regex=True)]
                    
                if verbose:
                    print(f"Found {len(keyword_holdings)} holdings related to '{search_keyword}' in {zip_file}")
                
                if not keyword_holdings.empty:
                    for index, row in keyword_holdings.iterrows():
                        holding_summary = {
                            'ACCESSION_NUMBER': row['ACCESSION_NUMBER'],
                            'HOLDING_ID': row['HOLDING_ID'],
                            'FILENAME_TIMESTAMP': timestamp,
                            'ISSUER_NAME': row['ISSUER_NAME'],
                            'ISSUER_LEI': row['ISSUER_LEI'],
                            'ISSUER_TITLE': row['ISSUER_TITLE'],
                            'ISSUER_CUSIP': row['ISSUER_CUSIP'],
                            'BALANCE': row['BALANCE'],
                            'UNIT': row['UNIT'],
                            'OTHER_UNIT_DESC': row['OTHER_UNIT_DESC'],
                            'CURRENCY_CODE': row['CURRENCY_CODE'],
                            'CURRENCY_VALUE': row['CURRENCY_VALUE'],
                            'EXCHANGE_RATE': row['EXCHANGE_RATE'],
                            'PERCENTAGE': row['PERCENTAGE'],
                            'PAYOFF_PROFILE': row['PAYOFF_PROFILE'],
                            'ASSET_CAT': row['ASSET_CAT'],
                            'OTHER_ASSET': row['OTHER_ASSET'],
                            'ISSUER_TYPE': row['ISSUER_TYPE'],
                            'OTHER_ISSUER': row['OTHER_ISSUER'],
                            'INVESTMENT_COUNTRY': row['INVESTMENT_COUNTRY'],
                            'IS_RESTRICTED_SECURITY': row['IS_RESTRICTED_SECURITY'],
                            'FAIR_VALUE_LEVEL': row['FAIR_VALUE_LEVEL'],
                            'DERIVATIVE_CAT': row['DERIVATIVE_CAT'],
                        }
                        
                        # Process additional TSV files for each holding
                        for tsv_name in ['REGISTRANT', 'FUND_REPORTED_INFO', 'INTEREST_RATE_RISK', 'BORROWER', 'BORROW_AGGREGATE', 'MONTHLY_TOTAL_RETURN', 'MONTHLY_RETURN_CAT_INSTRUMENT', 'IDENTIFIERS']:
                            try:
                                with zip_ref.open(f'{tsv_name}.tsv') as tsvfile:
                                    df = pd.read_csv(tsvfile, delimiter='\t', low_memory=False)
                                    if tsv_name == 'REGISTRANT':
                                        reg_row = df[df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']]
                                        if not reg_row.empty:
                                            for col in ['CIK', 'REGISTRANT_NAME', 'FILE_NUM', 'LEI', 'ADDRESS1', 'ADDRESS2', 'CITY', 'STATE', 'COUNTRY', 'ZIP', 'PHONE']:
                                                if col in reg_row.columns:
                                                    holding_summary[col] = reg_row.iloc[0][col]
                                    elif tsv_name == 'FUND_REPORTED_INFO':
                                        fund_row = df[df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']]
                                        if not fund_row.empty:
                                            for col in fund_row.columns:
                                                if col not in holding_summary:
                                                    holding_summary[col] = fund_row.iloc[0][col]
                                    elif tsv_name == 'INTEREST_RATE_RISK':
                                        intrst_rate_row = df[df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']]
                                        if not intrst_rate_row.empty:
                                            for col in intrst_rate_row.columns:
                                                if col not in holding_summary:
                                                    holding_summary[col] = intrst_rate_row.iloc[0][col]
                                    elif tsv_name == 'BORROWER':
                                        borrower_row = df[df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']]
                                        if not borrower_row.empty:
                                            for col in ['NAME', 'LEI', 'AGGREGATE_VALUE']:
                                                if col in borrower_row.columns:
                                                    holding_summary[f"BORROWER_{col}"] = borrower_row.iloc[0][col]
                                    elif tsv_name == 'BORROW_AGGREGATE':
                                        borrow_agg_row = df[df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']]
                                        if not borrow_agg_row.empty:
                                            for col in ['AMOUNT', 'COLLATERAL', 'INVESTMENT_CAT', 'OTHER_DESC']:
                                                if col in borrow_agg_row.columns:
                                                    holding_summary[f"BORROW_AGGREGATE_{col}"] = borrow_agg_row.iloc[0][col]
                                    elif tsv_name == 'MONTHLY_TOTAL_RETURN':
                                        mtr_row = df[df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']]
                                        if not mtr_row.empty:
                                            for i in range(1, 4):  # 1, 2, 3 for the three months
                                                holding_summary[f'MONTHLY_TOTAL_RETURN_{i}'] = mtr_row.iloc[0][f'MONTHLY_TOTAL_RETURN{i}']
                                    elif tsv_name == 'MONTHLY_RETURN_CAT_INSTRUMENT':
                                        mrci_row = df[(df['ACCESSION_NUMBER'] == row['ACCESSION_NUMBER']) & 
                                                      (df['ASSET_CAT'] == row['ASSET_CAT'])]
                                        if not mrci_row.empty:
                                            for i in range(1, 4):  # 1, 2, 3 for the three months
                                                for prefix in ['NET_REALIZED_GAIN', 'NET_UNREALIZED_AP']:
                                                    holding_summary[f'{prefix}_MON{i}'] = mrci_row.iloc[0][f'{prefix}_MON{i}']
                                    elif tsv_name == 'IDENTIFIERS':
                                        identifiers_row = df[df['HOLDING_ID'] == row['HOLDING_ID']]
                                        if not identifiers_row.empty:
                                            for col in ['IDENTIFIER_ISIN', 'IDENTIFIER_TICKER', 'OTHER_IDENTIFIER', 'OTHER_IDENTIFIER_DESC']:
                                                if col in identifiers_row.columns:
                                                    holding_summary[col] = identifiers_row.iloc[0][col]

                            except KeyError:
                                if verbose:
                                    print(f"Could not find {tsv_name} for {row['ACCESSION_NUMBER']}")

                        # Add quarterly data
                        if 'REPORT_DATE' in holding_summary:
                            holding_summary['YYYYQQ'] = f"{holding_summary['REPORT_DATE'].year}Q{((holding_summary['REPORT_DATE'].month-1)//3) + 1}"
                        else:
                            holding_summary['YYYYQQ'] = None

                        summary.append(holding_summary)
                        #if verbose and index % 10 == 0:  # Print status every 10 entries
                        #    print(f"Processed {index} holdings for {zip_file}")
        if verbose:
            print(f"Finished {zip_file}")
    except Exception as e:
        if verbose:
            print(f"Error processing {zip_file}: {str(e)}")
    
    return summary
def process_file(zip_file, search_terms, verbose=False, looking_for_swaps=False):
    results = []
    for term in search_terms:
        if term == 'SWAPS$':
            summary, _ = search_nport_swaps(zip_file, verbose, debug=True)
        else:
            summary = main_search(zip_file, term, verbose, looking_for_swaps)
        
        # Convert to datetime if needed
        for item in summary:
            date = datetime.fromtimestamp(item['FILENAME_TIMESTAMP']) if 'FILENAME_TIMESTAMP' in item else datetime(1970, 1, 1)
            results.append((date, item))
    return results
def list_csv_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('_results.csv')]
def write_to_csv(queue, output_file, verbose=False):
    with open(output_file, 'w', newline='') as csvfile:
        writer = pd.DataFrame().to_csv(csvfile, index=False, header=True, mode='w')  # Write header once
        while True:
            try:
                date, item = queue.get(timeout=1)  # Wait up to 1 second
                if date is None:  # Sentinel value to signal end of queue
                    break
                df = pd.DataFrame([item])
                df.to_csv(csvfile, index=False, header=False, mode='a')
                if verbose:
                    print(f"Wrote item with date {date} to CSV")
            except Empty:
                if verbose:
                    print("No more items to write, writer thread exiting.")
                break
            except Exception as e:
                if verbose:
                    print(f"Error writing to CSV: {e}")
def count():
    from collections import defaultdict
    import os
    import glob
    from zipfile import ZipFile
    import pandas as pd
    import logging
    from datetime import datetime
    import gc

    gamecat_ascii()

    # Set up logging
    log_file = os.path.join(EQUITY_SOURCE_DIR, 'count_process.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    def parse_zips(search_term=None):
        from collections import defaultdict
        import os
        import glob
        from zipfile import ZipFile
        import pandas as pd
        import logging
        from datetime import datetime
        import gc

        # Set up logging
        log_file = os.path.join(EQUITY_SOURCE_DIR, 'count_process.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Initialize output CSV with headers
        master_csv_path = os.path.join(EQUITY_SOURCE_DIR, 'date_notional_summary_by_all_currencies.csv')
        known_currencies = {'EUR', 'USD', 'JPY', 'CAD', 'AUD', 'CHF'}
        all_currencies = set(known_currencies)  # Will grow with unknown currencies

        # Define headers based on search term
        is_perpetual = search_term == '9999-12-31'
        if is_perpetual:
            initial_columns = ['Count', 'NEWT', 'MODI', 'Date'] + sorted(list(all_currencies))
        else:
            initial_columns = ['Count', 'Date'] + sorted(list(all_currencies))
        
        # Initialize CSV
        pd.DataFrame(columns=initial_columns).to_csv(master_csv_path, index=False, mode='w')
        logging.info(f"Initialized CSV with {len(initial_columns)} headers: {master_csv_path}")

        # Get and sort ZIP files
        zip_files = sorted(glob.glob(os.path.join(EQUITY_SOURCE_DIR, '*.zip')), key=lambda x: os.path.basename(x))
        total_files = len(zip_files)
        files_processed = 0

        # Load processed files from log to skip them if resuming
        processed_files = set()
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                for line in f:
                    if 'Successfully processed' in line:
                        file_path = line.split('Successfully processed ')[-1].split(' at')[0].strip()
                        processed_files.add(os.path.normpath(file_path))

        print(f"\nStarting to process {total_files} zip files...")
        logging.info(f"Starting to process {total_files} zip files")

        for index, zip_file in enumerate(zip_files, 1):
            zip_file = os.path.normpath(zip_file)
            if zip_file in processed_files:
                print(f"Skipping already processed file {index}/{total_files}: {zip_file}")
                logging.info(f"Skipped already processed file: {zip_file}")
                continue

            print(f"\nProcessing file {index}/{total_files}: {zip_file}")
            logging.info(f"Processing file: {zip_file}")

            # Initialize aggregates for this file
            date_aggregates = {}
            try:
                with ZipFile(zip_file, 'r') as zip_ref:
                    csv_filename = zip_ref.namelist()[0]  # Assuming one CSV per zip
                    print(f"Reading CSV file: {csv_filename}")
                    logging.info(f"Reading CSV file: {csv_filename}")
                    with zip_ref.open(csv_filename) as csv_file:
                        df = pd.read_csv(csv_file, low_memory=False)
                        # Check if required columns exist (C:2, L:11, M:12, T:19, V:21)
                        if len(df.columns) <= 21:  # Need at least 22 columns
                            print(f"Warning: {zip_file} has fewer than 22 columns. Skipping.")
                            logging.warning(f"{zip_file} has fewer than 22 columns. Skipping.")
                            continue
                        column_c = df.iloc[:, 2]   # Column C (TYPE: NEWT, MODI, etc.)
                        column_l = df.iloc[:, 11]  # Column L (effective dates)
                        column_m = df.iloc[:, 12]  # Column M (expiry dates)
                        column_t = df.iloc[:, 19]  # Column T (notional amounts)
                        column_v = df.iloc[:, 21]  # Column V (currency type)

                        # Convert notional amounts to numeric
                        column_t_numeric = pd.to_numeric(column_t, errors='coerce')
                        if column_t_numeric.isna().all():
                            print(f"Warning: No valid numeric values in column T of {zip_file}. Skipping.")
                            logging.warning(f"No valid numeric values in column T of {zip_file}. Skipping.")
                            continue

                        if is_perpetual:
                            # Filter for perpetual swaps (Column M == '9999-12-31')
                            perpetual_mask = column_m == '9999-12-31'
                            df_perpetual = df[perpetual_mask]
                            if df_perpetual.empty:
                                print(f"No perpetual swaps found in {zip_file}. Skipping.")
                                logging.info(f"No perpetual swaps found in {zip_file}.")
                                continue
                            
                            # Aggregate by effective date (Column L)
                            for date, type_val, notional, currency in zip(
                                df_perpetual.iloc[:, 11],  # Column L
                                df_perpetual.iloc[:, 2],   # Column C
                                pd.to_numeric(df_perpetual.iloc[:, 19], errors='coerce'),  # Column T
                                df_perpetual.iloc[:, 21]   # Column V
                            ):
                                if pd.notna(date) and isinstance(date, str) and len(date) == 10:
                                    try:
                                        datetime.strptime(date, '%Y-%m-%d')  # Validate date
                                        if date not in date_aggregates:
                                            date_aggregates[date] = {
                                                'count': 0,
                                                'newt': 0,
                                                'modi': 0,
                                                'notional': defaultdict(float)
                                            }
                                        date_aggregates[date]['count'] += 1
                                        if type_val == 'NEWT':
                                            date_aggregates[date]['newt'] += 1
                                        elif type_val == 'MODI':
                                            date_aggregates[date]['modi'] += 1
                                        if pd.notna(notional):
                                            currency = str(currency).strip().upper()
                                            date_aggregates[date]['notional'][currency] += notional
                                            all_currencies.add(currency)
                                    except ValueError:
                                        print(f"Warning: Invalid date format in {zip_file} for value {date}. Skipping.")
                                        logging.warning(f"Invalid date format in {zip_file} for value {date}. Skipping.")
                                else:
                                    print(f"Warning: Skipping invalid date {date} in {zip_file}.")
                                    logging.warning(f"Skipping invalid date {date} in {zip_file}.")
                        else:
                            # Default mode: Aggregate by expiry date (Column M)
                            for date, notional, currency in zip(column_m, column_t_numeric, column_v):
                                if pd.notna(date) and isinstance(date, str) and len(date) == 10:
                                    try:
                                        datetime.strptime(date, '%Y-%m-%d')
                                        if date not in date_aggregates:
                                            date_aggregates[date] = {
                                                'count': 0,
                                                'notional': defaultdict(float)
                                            }
                                        date_aggregates[date]['count'] += 1
                                        if pd.notna(notional):
                                            currency = str(currency).strip().upper()
                                            date_aggregates[date]['notional'][currency] += notional
                                            all_currencies.add(currency)
                                    except ValueError:
                                        print(f"Warning: Invalid date format in {zip_file} for value {date}. Skipping.")
                                        logging.warning(f"Invalid date format in {zip_file} for value {date}. Skipping.")
                                else:
                                    print(f"Warning: Skipping invalid date {date} in {zip_file}.")
                                    logging.warning(f"Skipping invalid date {date} in {zip_file}.")

                    # Convert aggregates to DataFrame for this file
                    if date_aggregates:
                        result_data = []
                        current_columns = ['Count', 'NEWT', 'MODI', 'Date'] if is_perpetual else ['Count', 'Date']
                        current_columns += sorted(list(all_currencies))
                        for date, data in date_aggregates.items():
                            row = {'Date': date, 'Count': data['count']}
                            if is_perpetual:
                                row['NEWT'] = data['newt']
                                row['MODI'] = data['modi']
                            # Fill all known currencies with 0 if not present
                            for currency in all_currencies:
                                row[currency] = data['notional'].get(currency, 0)
                            result_data.append(row)
                        result_df = pd.DataFrame(result_data, columns=current_columns)

                        # Append to CSV with updated header if new currencies are detected
                        if os.path.exists(master_csv_path):
                            existing_df = pd.read_csv(master_csv_path, nrows=0)
                            existing_columns = set(existing_df.columns)
                            new_columns = set(current_columns) - existing_columns
                            if new_columns:
                                logging.info(f"Detected new currencies: {new_columns}. Updating CSV header.")
                                # Append new columns with 0 to existing data
                                with open(master_csv_path, 'a') as f:
                                    for _ in range(len(existing_df.index)):
                                        f.write(',' + ','.join(['0'] * len(new_columns)) + '\n')
                                # Rewrite header with all columns
                                result_df.to_csv(master_csv_path, index=False, mode='w')
                            else:
                                result_df.to_csv(master_csv_path, index=False, header=False, mode='a')
                        else:
                            result_df.to_csv(master_csv_path, index=False, mode='w')

                        print(f"Appended results for {zip_file} to {master_csv_path}")
                        logging.info(f"Appended results for {zip_file} to {master_csv_path}")

                        # Log number of unique dates before clearing
                        num_dates = len(date_aggregates)
                        # Clear memory
                        del result_df
                        del date_aggregates
                        gc.collect()
                    else:
                        num_dates = 0
                        logging.info(f"No valid data aggregated for {zip_file}.")

                    files_processed += 1
                    print(f"Processed {zip_file}. Current aggregates: {num_dates} unique dates.")
                    logging.info(f"Successfully processed {zip_file} at {datetime.now()}")
            except Exception as e:
                logging.error(f"Error processing {zip_file}: {e}")
                print(f"Error occurred while processing {zip_file}. Continuing to next file.")

        print(f"\nProcessing complete. Total files processed: {files_processed}/{total_files}")
        logging.info(f"Processing complete. Total files processed: {files_processed}/{total_files}")

        # Load final CSV to compute totals
        if files_processed > 0:
            final_df = pd.read_csv(master_csv_path, on_bad_lines='skip', encoding='utf-8')
            if not final_df.empty:
                total_count = final_df['Count'].sum()
                total_notional_by_currency = {c: final_df[c].sum() for c in all_currencies if c in final_df.columns}
                print(f"Total count of dates: {total_count}")
                if is_perpetual:
                    total_newt = final_df['NEWT'].sum() if 'NEWT' in final_df.columns else 0
                    total_modi = final_df['MODI'].sum() if 'MODI' in final_df.columns else 0
                    print(f"Total NEWT count: {total_newt}")
                    print(f"Total MODI count: {total_modi}")
                for currency, total in total_notional_by_currency.items():
                    print(f"Total {currency} notional: {total:.2f}")
                logging.info(f"Column {'L' if is_perpetual else 'M'} count and Notional T sum by currency completed. Total count: {total_count}")
            else:
                print("No valid data found.")
                logging.info("No valid data found for aggregation.")
            return final_df
        else:
            print("No valid data found.")
            logging.info("No valid data found for aggregation.")
            return pd.DataFrame(columns=initial_columns)

    print("Enter a date to filter (e.g., 2023-01-01) or 9999-12-31 for perpetual swaps, or 'q' to quit:")
    user_input = input().strip()
    if user_input.lower() != 'q':
        search_term = user_input if user_input else None
        result_df = parse_zips(search_term=search_term)
        if not result_df.empty:
            master_csv_path = os.path.join(EQUITY_SOURCE_DIR, 'date_notional_summary_by_all_currencies.csv')
            print(f"\nSaving results to: {master_csv_path}")
            if search_term == '9999-12-31':
                print(f"CSV columns: A (Count), B (NEWT), C (MODI), D (Date), followed by columns for each currency (e.g., E (AUD), F (CAD), ...)")
            else:
                print(f"CSV columns: A (Count), B (Date), followed by columns for each currency (e.g., C (AUD), D (CAD), ...)")
        else:
            print("No data to save.")
    else:
        print("Exiting script.")
if __name__ == "__main__":
    check_and_install_modules()
    import_modules()
    gamecock_ascii()    
    # Display numbered prompt for archive type selection
    print("Which archives would you like to download?")
    print("6: N-PORT archives")
    print("9: N-CEN archives")
    print("4: Form D archives")
    print("2: NMFP archives")
    print("0: 13F archives")
    print("g: SEC Credit Swap archives")
    print("g2: SEC Equity Swap archives")
    print("m: CFTC Credit Swap archives")
    print("m2: CFTC Equity Swap archives")
    print("m3: CFTC Commodity Swap archives")
    print("m4: CFTC Foreign Exchange Swap archives")
    print("m5: CFTC Interest Rate Swap archives")
    print("e: Edgar archives")
    print("r: Exchange volume archives")
    print("i: Insider trading archives")
    print("c: Codex Of Instruments")
    print("a: Allyourbasearebelongtous- scrape every edgar filing ever.")

    query = input("Enter the number corresponding to your choice: ").strip()
    if query.isdigit() and len(query) == 7:
        process_cik(query)  # Call it directly
    if query == 'count':
        count()
    if query == '6':
        download_nport_archives()
        search_keyword = input("Enter the keyword to search for (e.g., 'Gamestop'): ").strip() or 'gamestop'
        verbose = input("Enable verbose mode? (y/n): ").lower() == 'y'
        search_nport(search_keyword, verbose)
    elif query == '9':
        download_ncen_archives()
        search_keywords = input("Enter the keyword to search for (e.g., 'Gamestop'): ").strip() or 'gamestop'
        verbose = input("Enable verbose mode? (y/n): ").lower() == 'y'
        search_ncen(search_keywords, verbose=verbose)
    elif query == '4':
        download_formd_archives()
    elif query == '2':
        download_nmfp_archives()
        search_keywords = input("Enter the keyword to search for (e.g., 'Gamestop'): ").strip() or 'gamestop'
        verbose = input("Enable verbose mode? (y/n): ").lower() == 'y'
        search_nmfp(search_keywords, verbose=False)
    elif query == '0':
        download_13F_archives()
    elif query == 'g':
        download_credit_archives()
    elif query == 'g2':
        download_equities_archives()
    elif query == 'm':
        download_cftc_credit_archives()
    elif query == 'm2':
        download_cftc_equities_archives()
    elif query == 'm3':
        download_cftc_commodities_archives()
    elif query == 'm4':
        download_cftc_forex_archives()
    elif query == 'm5':
        download_cftc_rates_archives()
    elif query == 'e':
        # Download Edgar Archives
        download_edgar_archives()
        while True:
            print("\nWhat would you like to do with the downloaded Edgar archives?")
            print("1: Search the archives for a company name")
            print("2: Scrape Edgar for filings based on a CIK")
            print("3: Download filings using existing search results")
            print("0: Exit to main menu")
            
            choice = input("Enter your choice (0-3): ").strip()
            if choice == '0':
                break
            
            elif choice == '1':
                edgar_second()
            
            elif choice == '2':
                cik = input("Enter the CIK to scrape (e.g., '0000320193' for Apple): ").strip()
                if cik.isdigit() and 1 <= len(cik) <= 10:  # Validate CIK length
                    # Use original functions for scraping
                    sec_url_full = f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                    print(f"Embarking on the quest for {sec_url_full}...")
                    base_download_dir = EDGAR_SOURCE_DIR
                    folder_name = sec_url_full.rstrip('/').split('/')[-1]
                    full_download_directory = os.path.join(base_download_dir, folder_name)
                    print(f"Full download directory: {full_download_directory} - Here lies our treasure vault")

                    subdirectories = scrape_subdirectories(sec_url_full)
                    if not subdirectories:
                        print(f"No hidden chambers found at {sec_url_full}. Exiting this quest.")
                        continue

                    full_subdirectory_urls = [f"{sec_url_full.rstrip('/')}/{sub}" for sub in subdirectories]
                    
                    sanitized_file_path = 'sanitized_subdirectories.txt'
                    with open(sanitized_file_path, 'w') as sanitized_file:
                        sanitized_file.write('\n'.join(full_subdirectory_urls))
                    print(f"Sanitized list created: {sanitized_file_path} - The map to hidden chambers is drawn")

                    output_file_path = 'completed_subdirectories.txt'
                    if os.path.exists(output_file_path):
                        with open(output_file_path, 'r') as file:
                            completed_subdirectories = [line.strip() for line in file]
                    else:
                        completed_subdirectories = []

                    os.makedirs(full_download_directory, exist_ok=True)
                    print(f"Download directory created: {full_download_directory} - The vault is ready to receive its riches")

                    total_subdirectories = len(full_subdirectory_urls)
                    processed_subdirectories = len(completed_subdirectories)
                    rows = []  # List to store download results

                    for subdirectory in full_subdirectory_urls:
                        if subdirectory in completed_subdirectories:
                            print(f"Skipping already plundered chamber: {subdirectory}")
                            continue

                        print(f"Venturing into the chamber: {subdirectory}")
                        try:
                            soup = fetch_directory(subdirectory)
                            txt_links = extract_txt_links(soup)
                            print(f"Found txt links in {subdirectory}: {txt_links} - Scrolls of lore discovered")
                            for txt_link in txt_links:
                                txt_url = "https://www.sec.gov" + txt_link
                                print(f"Downloading txt file: {txt_url} - Securing the scroll")
                                download_success = download_file(txt_url, full_download_directory)
                                download_location = os.path.join(full_download_directory, os.path.basename(txt_url)) if download_success else 'Failed'
                                rows.append([cik, txt_url, download_location, 'Success' if download_success else 'Failed'])
                                if download_success:
                                    with open(output_file_path, 'a') as completed_file:
                                        completed_file.write(subdirectory + '\n')
                                    break
                                time.sleep(0.1)  # Avoid rate limiting
                        except Exception as e:
                            print(f"Failed to access {subdirectory}: {e} - Beware, for this path is cursed!")
                            with open('error_log.txt', 'a') as error_log_file:
                                error_log_file.write(f"Failed to access {subdirectory}: {e}\n")

                        processed_subdirectories += 1
                        print(f"Progress: {processed_subdirectories}/{total_subdirectories} chambers explored.")

                    remaining_subdirectories = [sub for sub in full_subdirectory_urls if sub not in completed_subdirectories]
                    with open(sanitized_file_path, 'w') as sanitized_file:
                        sanitized_file.write('\n'.join(remaining_subdirectories))

                    # Create CSV and HTML output
                    csv_file = os.path.join(EDGAR_SOURCE_DIR, f"{cik}_scraped_results.csv")
                    with open(csv_file, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['CIK', 'URL', 'Download Location', 'Status'])
                        writer.writerows(rows)
                    html_file = os.path.join(EDGAR_SOURCE_DIR, f"{cik}_scraped_index.html")
                    with open(html_file, 'w', encoding='utf-8') as htmlfile:
                        htmlfile.write('<!DOCTYPE html><html><head><title>Scraped Index</title></head><body><table border="1">')
                        htmlfile.write('<tr>' + ''.join(f'<th>{h}</th>' for h in ['CIK', 'URL', 'Download Location', 'Status']) + '</tr>')
                        for row in rows:
                            htmlfile.write('<tr>')
                            for item in row:
                                if item.startswith('./edgar') or item == 'Failed':
                                    htmlfile.write(f'<td><a href="file://{os.path.abspath(item)}">{item}</a></td>' if item != 'Failed' else f'<td>{item}</td>')
                                else:
                                    htmlfile.write(f'<td><a href="{item}">{item}</a></td>')
                            htmlfile.write('</tr>')
                        htmlfile.write('</table></body></html>')
                    print(f"Scraping complete. Results saved to {csv_file} and {html_file}")
                else:
                    print("Invalid CIK. Please enter a 10- or 12-digit number.")
            
            elif choice == '3':
                csv_files = list_csv_files(EDGAR_SOURCE_DIR)
                if not csv_files:
                    print("No CSV files found. Please search the archives first (option 1).")
                    continue
                print("Available CSV files (without '_results.csv'):")
                for i, file in enumerate(csv_files):
                    print(f"{i + 1}: {file[:-len('_results.csv')]}")
                while True:
                    file_choice = input("Select a CSV file by number (or '0' to return to menu): ").strip()
                    if file_choice == '0':
                        break
                    try:
                        file_choice = int(file_choice)
                        if 1 <= file_choice <= len(csv_files):
                            csv_file = csv_files[file_choice - 1]
                            method = input("Use 'url' or 'crawl' method: ").strip().lower()
                            if method in ['url', 'crawl']:
                                edgar_third(csv_file, method)
                                repeat = input("Process another CSV? (yes/no): ").strip().lower()
                                if repeat != 'yes':
                                    break
                            else:
                                print("Please enter 'url' or 'crawl'.")
                        else:
                            print("Invalid choice.")
                    except ValueError:
                        print("Please enter a valid number.")
            
            else:
                print("Invalid choice. Please enter 0-3.")
    elif query == 'r':
        download_exchange_archives()
    elif query == 'i':
        download_insider_archives()
    elif query == 'c':
        codex()
    elif query == 'a':
        allyourbasearebelongtous()
    else:
        print("Invalid input. Please enter one of the following: 69420gmerica.")
        exit(1)