from sys import getsizeof
import core.log as logging
from numerize.numerize import numerize
from playwright.sync_api import sync_playwright

log = logging.root.new_logger('grabber')

def open_browser(core: sync_playwright, idle: bool = False, headless: bool = True) -> object:
    
    log.log('Booting core grabber')
    
    return core.firefox.launch_persistent_context(
            headless = headless,
            args = [
                '--mute-audio',
                '--allow-legacy-extension-manifests '
            ],
            
            ignore_default_args = [
                '--disable-extensions',
            ],
            
            user_data_dir = './chrome/',
            
            has_touch = True,
            is_mobile = True,
            devtools = True
        )

def grab_request(url: str, headless: bool = True) -> str:
    '''
    Get the list of providing urls from a provider.
    (fusenet and *theorically* pstream).
    -----------------------------------------------
    
    Arguments
        url: the provider url.
        debug: whether to debug.
        headless: whether to use headless mode.
    '''
    
    x, y = 800, 600
    
    with sync_playwright() as core:
        
        # Setup
        browser = open_browser(core, False, headless)
        
        page = browser.new_page()
        page.set_viewport_size({'width': x, 'height': y})
        
        page.goto(url)
        page.wait_for_load_state()
        
        # Play media
        page.tap('html', position = {'x': x / 2, 'y': y / 2})
        
        log.log('Listenning for requests...')
        
        # Wait for quality request (m method)
        with page.expect_request_finished(lambda req: '//fusevideo.net/m/' in req.response().url) as info:
            
            res = info.value.response().text()
            
            rep = info.value.response().url.split('/m/')[1][:20] + '...'
            log.log(f'Grabbed request \033[92m{rep}\033[0m (\033[95m{numerize(getsizeof(res))}o\033[0m)')
            
            browser.close()
            return res

def setup() -> None:
    '''
    Open the browser wihtout context.
    '''
    
    log.warn('Started browser in setup mode')
    
    with sync_playwright() as core:
        
        # Init browser
        browser: core.firefox.launch = open_browser(core, False, False)
        
        # Idle
        while 1: pass

# EOF