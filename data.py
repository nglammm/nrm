import urllib3

def main():
    http = urllib3.PoolManager()

    pastebin_url = "https://pastejustit.com/raw/bwlexyxpd7"

    try:
        response = http.request('GET', pastebin_url)
        # Check if the request was successful
        if response.status == 200:
            # Create or overwrite the .env file
            with open('.env', 'w') as env_file:
                env_file.write(response.data.decode('utf-8'))
        else:
            print(f"Failed to retrieve data from Pastebin. Status code: {response.status}")

    except Exception as e:
        print(f"An error occurred: {e}")