import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    urls = []
    
    print("==================================================")
    print(" Enter the URLs you want to scan for PDFs.")
    print(" Type 'done' and press Enter when you are finished.")
    print("==================================================")

    # collect multiple URLs from the user
    while True:
        user_input = input(f"URL #{len(urls) + 1}: ").strip()
        
        if user_input.lower() == "done":
            if not urls:
                print("You didn't enter any URLs! Exiting.")
                return
            break
        
        if user_input:
            # Quick protocol formatting check
            if not user_input.startswith(("http://", "https://")):
                user_input = "https://" + user_input
            urls.append(user_input)

    print(f"\nLoaded {len(urls)} target(s). Launching Firefox...")

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()

        # Create downloads directory
        download_dir = "./downloads"
        os.makedirs(download_dir, exist_ok=True)

        # Define the network response sniffer
        async def handle_response(response):
            url = response.url
            is_pdf_url = ".pdf" in url.lower()
            headers = response.headers
            is_pdf_header = "application/pdf" in headers.get("content-type", "").lower()

            if is_pdf_url or is_pdf_header:
                print(f"  [!] Found PDF Request: {url[:75]}...")
                try:
                    if response.status == 200:
                        filename = url.split("/")[-1].split("?")[0]
                        if not filename.endswith(".pdf") or len(filename) < 5:
                            filename = f"downloaded_{int(asyncio.get_event_loop().time())}.pdf"
                        
                        filepath = os.path.join(download_dir, filename)
                        
                        pdf_buffer = await response.body()
                        with open(filepath, "wb") as f:
                            f.write(pdf_buffer)
                            
                        print(f"  [✔] Saved to: {filepath}")
                    else:
                        print(f"  [✘] Failed (Status: {response.status})")
                except Exception as e:
                    print(f"  [✘] Error saving data: {e}")

        # Bind the background network scanner
        page.on("response", lambda response: asyncio.create_task(handle_response(response)))

        #Process each URL sequentially
        for idx, target_url in enumerate(urls, 1):
            print(f"\n[{idx}/{len(urls)}] Processing: {target_url}")
            
            try:
                # networkidle keeps the browser on the page until traffic settles down
                await page.goto(target_url, wait_until="networkidle", timeout=45000)
                # Brief pause to ensure any triggered asynchronous requests finish writing
                await asyncio.sleep(1.5)
            except Exception:
                # Catching navigation timeouts/errors gracefully so the loop doesn't break
                print("  [i] Moving on (Page load finalized or intercepted)")
                await asyncio.sleep(1.5)

        await browser.close()
        print("\n==================================================")
        print("All targets processed. Browser closed.")
        print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())