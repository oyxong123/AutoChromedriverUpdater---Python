def main():
    import requests
    import os
    import time
    import shutil
    import zipfile    
    import elevate
    import platform as platform_lib
    import urllib
    import urllib.request
    from selenium import webdriver
    from win10toast_persist import ToastNotifier

    # Wait for chromedriver file to finish download in specified path.
    def wait_and_get_path_of_chromedriver_file_downloaded(path: str, nameFile: str) -> str:
        fileNames = []
        filesWithKeywords = []
        keywordDownloaded = [nameFile]
        initialBufferTime = 3
        subsequentBufferTime = 1
        loopCount = 0
        time.sleep(initialBufferTime)   
        while True:
            fileNames = os.listdir(path)
            filesWithKeywords = [y for x in keywordDownloaded for y in fileNames if x in y]  # Checks if any of the file names contain the keywords as substring and make them into a list.
            
            # End wait if the correct file has been downloaded.
            if filesWithKeywords != []:
                return
            
                """ 
                # Return the latest downloaded chromedriver file's path.
                pathFileDownloadedLatest = ""
                dateFileDownloadedLatest = "0"
                for fileName in filesWithKeywords:
                    pathFile = f"{path}/{fileName}"
                    dateLatest = os.path.getctime(pathFile)
                    if dateLatest > dateFileDownloadedLatest:
                        pathFileDownloadedLatest = pathFile
                        dateFileDownloadedLatest = dateLatest
                return pathFileDownloadedLatest
                """    
                 
            # Set timeout duration.
            if loopCount >= 50:  
                raise Exception("No downloaded chromedriver file found.")
        
            # Prepare for next loop to find downloaded chromedriver file's path.
            time.sleep(subsequentBufferTime)
            loopCount += 1
        
    # Do own manual implementation of api call to CtF Json API endpoint.
    try:
        # Toast message to notify script started.
        print("Auto Chromedriver operation start.")
        notif = ToastNotifier()
        notif.show_toast("Auto Chromedriver Updater", f"Operation started.", duration=5)
        
        # Ensure all important paths exist and are empty.
        loggedInUser = os.getlogin()
        pathDownload = f"C:/Users/{loggedInUser}/Downloads"
        if not os.path.exists(pathDownload):
            raise Exception("Downloads directory not found")
        
        # Call CfT json api endpoint. 
        print("Calling CfT JSON API endpoint.")
        url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"  # Contains both latest version info + download links.
        response = requests.get(url)
        json = response.json()
        driverStable = json['channels']['Stable']
        versionLatest = driverStable['version']
        
        # Check current installed chromedriver version then compare and check whether it's the same version.
        print("Comparing current chromedriver version.")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") 
        driver = webdriver.Chrome(options)
        versionLocal = driver.capabilities['browserVersion']
        print(f"Local chromedriver version: {versionLocal}")
        print(f"Latest chromedriver version: {versionLatest}")
        
        if versionLocal != versionLatest:    
            # Check computer platform and 32/64 bit.
            print("Checking computer platform.")
            platform = ""
            system = platform_lib.system()
            if system == "Windows":
                bit = platform_lib.architecture()[0]
                if bit == "64bit":
                    bit = "64"
                elif bit == "32bit":
                    bit = "32"
                platform = f"win{bit}"
                del bit
            elif system == "linux":
                platform = "linux64"
            elif system == " Mac OS X":
                processor = platform_lib.processor()
                if processor == "arm":
                    platform = "mac-arm64"
                else:
                    platform = "mac-x64"
            
            # Get corresponding index for specific computer platform.
            platformIndex = 4
            if platform == "linux64":
                platformIndex = 0
            if platform == "mac-arm64":
                platformIndex = 1
            if platform == "mac-x64":
                platformIndex = 2
            if platform == "win32":
                platformIndex = 3
            if platform == "win64":
                platformIndex = 4
                
            # Allocate correct download link for the corresponding platform.
            print("Downloading latest chromedriver file.")
            urlDownload = driverStable['downloads']['chromedriver'][platformIndex]['url'] 
            nameFile = f"chromedriver-{platform}.zip"
            pathDownloadFile = f"{pathDownload}/{nameFile}"
            urllib.request.urlretrieve(urlDownload, pathDownloadFile)
            wait_and_get_path_of_chromedriver_file_downloaded(pathDownload, nameFile)
            
            # Extract the latest downloaded chromedriver zipfile.
            print("Extracting downloaded chromedriver file.")
            pathExtractingFrom = f"chromedriver-{platform}/chromedriver.exe"
            with zipfile.ZipFile(pathDownloadFile, 'r') as zippedFile:
                print(zippedFile.filelist)
                zippedFile.extract(pathExtractingFrom, pathDownload)
            pathChromedriverExtracted = f"{pathDownload}/{pathExtractingFrom}"
            if not os.path.exists(pathChromedriverExtracted):
                raise Exception("Extracted chromedriver file not found.")
            
            # Move the extracted chromedriver file to its dedicated location and overwrite it (by removing old one).
            print("Overwriting old chromedriver file.")
            pathChromedriverDefault = "C:/Windows/chromedriver.exe"
            pathWindowsFolder = "C:/Windows"
            if os.path.exists(pathChromedriverDefault):
                os.ch(pathChromedriverDefault, 0o777)
                os.remove(pathChromedriverDefault)
            shutil.move(pathChromedriverExtracted, pathWindowsFolder)
            
            # Delete all relevant files/dirs in Downloads dir.
            print("Deleting no-longer relevant files.")
            if not os.path.exists(pathDownloadFile):
                raise Exception("Unextracted chromedriver file to delete not found.")
            os.remove(pathDownloadFile)
            pathChromedriverFolderExtracted = f"{pathDownload}/chromedriver-{platform}"
            if not os.path.exists(pathChromedriverFolderExtracted):
                raise Exception("Extracted chromedriver folder to delete not found.")
            shutil.rmtree(pathChromedriverFolderExtracted, True)
        
        # Script completed declaration.
        scriptStatus = True
        
    except Exception as exception:
        # Set error details.
        scriptStatus = False
        errorMessage = str(exception)
        
        # Delete all relevant files/dirs in Downloads dir.
        if os.path.exists(pathDownloadFile):
            os.remove(pathDownloadFile)
        pathChromedriverFolderExtracted = f"{pathDownload}/chromedriver-{platform}"
        if os.path.exists(pathChromedriverFolderExtracted):
            shutil.rmtree(pathChromedriverFolderExtracted, True)

    # Add a notification to notify me about the success or failure.
    notif = ToastNotifier()
    if scriptStatus:
        notif.show_toast("Auto Chromedriver Updater", f"Chromedriver Updated.", duration=5)
        print("Script completed. Operation Success. Chromedriver Updated.") 
    else:
        notif.show_toast("Auto Chromedriver Updater", "Operation failed.\n" + errorMessage, duration=5)
        print("Script failed. Operation failed.\n" + errorMessage) 
    print("Terminating script.")
    time.sleep(10)

if __name__ == "__main__":
    main()