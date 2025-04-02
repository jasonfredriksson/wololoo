import asyncio
import json
import random
import time
import os
from playwright.async_api import async_playwright, Page

class InstagramPostReporter:
    """Class to handle Instagram post reporting automation with Playwright locators."""

    def __init__(self, page: Page):
        self.page = page

        #Locators
        # Login related
        self.login_link = self.page.locator("//span[contains(text(),'Inicia sesión')]").first
        self.username_input = self.page.locator("//input[@name='username']")
        self.password_input = self.page.locator("//input[@name='password']")
        self.login_button = self.page.locator("//div[contains(text(),'Iniciar sesión')]").first
        self.not_now_button = self.page.locator("//div[contains(text(),'Ahora no')]")
        self.not_now_button_alt = self.page.locator("//button[contains(text(), 'Ahora no')]")
        self.cookies_option = self.page.locator("//button[contains(text(), 'Rechazar cookies opcionales')]")
        
        # Post related
        self.post_items = self.page.locator("//div[@class='_aagw']")
        self.post_options_button = self.page.locator("//div[@class='_aasm']")
        self.report_button = self.page.locator("//button[contains(text(),'Reportar')]")
        self.close_button = self.page.locator("//button[contains(text(),'Cerrar')]")
        self.close_post_button = self.page.locator("//div[@class='x160vmok x10l6tqk x1eu8d0j x1vjfegm']")
        
        # Report reason locators
        self.scam_fraud_spam_option = self.page.locator("//*[contains(text(),'Estafa, fraude o spam')]")
        self.fraud_option = self.page.locator("//*[contains(text(),'Fraude o estafa')]")
        
        self.sale_promo_option = self.page.locator("//*[contains(text(),'Venta o promoción de artículos restringidos')]")
        self.what_sold_text = self.page.locator("//*[contains(text(),'¿Qué se vende o promociona?')]")
        self.drugs_option = self.page.locator("//*[contains(text(),'Drogas')][not(contains(text(),'Drogas altamente adictivas'))]")
        self.drug_type_text = self.page.locator("//*[contains(text(),'¿Qué tipo de drogas?')]")
        self.other_drugs_option = self.page.locator("//*[contains(text(),'Otras drogas')]")
        
        self.bullying_option = self.page.locator("//*[contains(text(),'Bullying o contacto no deseado')]")
        self.spam_option = self.page.locator("//*[contains(text(),'Spam')]")
        
        self.dislike_option = self.page.locator("//*[contains(text(),'Simplemente no me gusta')]")
        
        self.false_info_option = self.page.locator("//button//div[contains(text(),'Información falsa')]")
        self.what_false_info_text = self.page.locator("//*[contains(text(),'¿Qué tipo de información falsa?')]")
        self.health_option = self.page.locator("//div[contains(text(),'Salud')]")
        
        # Navigation
        self.home_button = self.page.locator("//span[contains(text(),'Inicio')]")
        self.more_options_button = self.page.locator("//span[contains(text(),'Más')]")
        self.logout_button = self.page.locator("//span[contains(text(),'Salir')]")
    
    def random_delay(self, min_sec=1, max_sec=3):
        """Generate a random delay to mimic human interaction."""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    def log_status(self, message):
        """Log a status message with timestamp."""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    async def navigate_to_profile(self, profile_url):
        """Navigate to the Instagram profile."""
        self.log_status(f"Navigating to: {profile_url}")
        await self.page.goto(profile_url)
        self.random_delay()
    
    async def accept_necessary_cookies(self):
        """Handle cookies dialog if it appears."""
        try:
            await self.cookies_option.click(timeout=5000)
            self.random_delay()
            self.log_status("Cookies dialog handled")
        except:
            self.log_status("No cookies dialog appeared")
    
    async def login(self, username, password):
        """Login to Instagram account."""
        self.log_status(f"Logging in as: {username}")
        
        try:
            async with self.page.expect_navigation():
                await self.login_link.click()
            self.random_delay()
        except Exception as e:
            self.log_status(f"Login navigation issue: {e}")
            # Try alternative approach for login
            try:
                await self.page.goto('https://www.instagram.com/accounts/login/')
                self.random_delay()
            except:
                self.log_status("Failed to navigate to login page directly")
        
        await self.username_input.fill(username)
        self.random_delay()
        
        await self.password_input.fill(password)
        self.random_delay()
        
        # Click the login button and wait for navigation
        try:
            async with self.page.expect_navigation():
                await self.login_button.click()
            self.random_delay()
        except Exception as e:
            self.log_status(f"Login button issue: {e}")
            # Try alternative login button selector
            try:
                login_alt = self.page.locator("//button[@type='submit']")
                async with self.page.expect_navigation():
                    await login_alt.click()
                self.random_delay()
            except:
                self.log_status("Failed to click alternative login button")
        
        # Handle "Save Login Info" dialog if it appears
        try:
            await self.not_now_button.click(timeout=5000)
            self.random_delay()
            self.log_status("Dismissed 'Save Login Info' dialog")
        except:
            self.log_status("No 'Save Login Info' dialog appeared")
    
    async def get_post_items(self):
        """Get all post items from the current profile."""
        self.log_status("Waiting for posts to load")
        await self.post_items.first.wait_for(state="visible")
        count = await self.post_items.count()
        self.log_status(f"Found {count} posts to process")
        return count
    
    async def report_post(self, post_index, action):
        """Report a post with the specified reason."""
        # Click on the post
        self.log_status(f"Opening post {post_index+1}")
        await self.post_items.nth(post_index).click()
        self.random_delay()
        
        # Click the options button
        self.log_status("Opening post options")
        await self.post_options_button.click()
        self.random_delay()
        
        # Click report button
        await self.report_button.click()
        self.random_delay(3, 5)  # Longer delay for report menu
        
        self.log_status(f"Reporting post for: {action}")
        
        # Handle different report reasons
        if action == "Estafa, fraude o spam":
            await self.scam_fraud_spam_option.click()
            await self.scam_fraud_spam_option.wait_for(state="detached", timeout=10000)
            self.random_delay()
            await self.fraud_option.click()
            self.random_delay()
            
        elif action == "Venta o promo":
            await self.sale_promo_option.click()
            await self.sale_promo_option.wait_for(state="detached", timeout=10000)
            await self.what_sold_text.wait_for(state="visible")
            self.random_delay()
            await self.drugs_option.click()
            await self.drugs_option.wait_for(state="detached", timeout=10000)
            await self.drug_type_text.wait_for(state="visible")
            self.random_delay()
            await self.other_drugs_option.click()
            await self.other_drugs_option.wait_for(state="detached", timeout=10000)
            self.random_delay()
            
        elif action == "Bullying o contacto no deseado":
            await self.bullying_option.click()
            self.random_delay()
            await self.spam_option.click()
            self.random_delay()
            
        elif action == "Simplemente no me gusta":
            await self.dislike_option.click()
            self.random_delay()
            
        elif action == "Info falsa":
            await self.false_info_option.click()
            await self.what_false_info_text.wait_for(state="visible")
            self.random_delay()
            await self.health_option.click()
            self.random_delay()
        
        # Close the report dialog
        await self.close_button.click()
        self.random_delay()
        self.log_status(f"Completed reporting for: {action}")
        
        # Close the post
        await self.close_post_button.click()
        self.random_delay()
    
    async def logout(self):
        """Logout from Instagram account."""
        self.log_status("Logging out")
        
        # Navigate to home
        await self.home_button.click()
        self.random_delay()
        
        # Handle notification dialog if it appears
        try:
            await self.not_now_button_alt.click(timeout=5000)
            self.random_delay()
        except:
            self.log_status("No notification dialog appeared")
        
        # Open more options
        await self.more_options_button.click()
        self.random_delay()
        
        # Click logout
        await self.logout_button.click()
        self.random_delay()
        self.log_status("Successfully logged out")


async def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'wololoo.json')
    
    # Load configuration from JSON
    with open(json_path, 'r') as file:
        config = json.load(file)
    
    # Initialize Playwright
    async with async_playwright() as p:
        # Process each set of credentials
        for creds in config['credentials']:
            # Launch browser
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Initialize our reporter class
            reporter = InstagramPostReporter(page)
            
            try:
                # Set the target Instagram profile
                target_profile = 'https://www.instagram.com/urmah.ar/'
                
                # Navigate to the profile
                await reporter.navigate_to_profile(target_profile)
                
                # Handle cookies if necessary
                await reporter.accept_necessary_cookies()
                
                # Login
                await reporter.login(creds['username'], creds['password'])
                
                # Navigate back to target profile after login
                await reporter.navigate_to_profile(target_profile)
                
                # Get post count
                post_count = await reporter.get_post_items()
                
                #report each post with each reason
                for post_index in range(min(post_count, 15)):  # For now, Limit to first 15 posts
                    for action in config['actions']:
                        await reporter.report_post(post_index, action)
                
                # Logout when finished
                await reporter.logout()
                
            except Exception as e:
                reporter.log_status(f"Error occurred: {e}")
            
            finally:
                # Always close the browser
                await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
