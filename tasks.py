from robocorp.tasks import task
from robocorp import browser
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import requests
from RPA.Assistant import Assistant


@task
def user_input_task():
    assistant = Assistant()
    assistant.add_heading("Input from user")
    assistant.add_text_input("text_input", placeholder="Please enter URL")
    assistant.add_submit_buttons("Submit", default="Submit")
    result = assistant.run_dialog()
    url = result.text_input
    order_robots_from_RobotSpareBin(url) 


def order_robots_from_RobotSpareBin(url):
    """Automated robot ordering process"""
    orders = get_orders()
    open_robot_order_website(url)
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        click_order_button()
        store_receipt_as_pdf(order["Order number"])
        click_order_another_robot_button()
    archive_receipts()


def get_orders():
    """
    Fetch orders from the given URL and return them as a table.

    Returns:
        table (list): List of orders.
    """
    url = "https://robotsparebinindustries.com/orders.csv"
    file = download_file(url, "orders.csv")
    library = Tables()
    table = library.read_table_from_csv("orders.csv")
    return table


def fill_the_form(order):
    """
    Fill the robot order form with the given order details.

    Args:
        order (dict): Dictionary containing order details.
    """
    page = browser.page()
    page.select_option("#head", order["Head"])
    page.set_checked(f"#id-body-{order['Body']}", checked=True)
    page.get_by_placeholder("Enter the part number for the legs").fill(order["Legs"])
    page.fill("#address", order["Address"])


def click_order_button():
    """
    Click the order button and verify if the order was successful.
    """
    page = browser.page()
    page.click('//*[@id="order"]')
    if page.is_visible('//*[@id="order-completion"]'):
        print("Order was successful")
    else:
        print("Error! Clicking again.")
        click_order_button()


def click_order_another_robot_button():
    """
    Click the button to order another robot.
    """
    page = browser.page()
    page.click('//*[@id="order-another"]')


def store_receipt_as_pdf(order_number):
    """
    Store the order receipt as a PDF file.

    Args:
        order_number (str): The order number for the receipt.
    """
    page = browser.page()
    receipt = page.locator('//*[@id="order-completion"]').inner_html()
    pdf = PDF()
    pdf_file = f"output/receipts/receipt-{order_number}.pdf"
    pdf.html_to_pdf(receipt, pdf_file)
    screenshot_file = f"output/screenshots/screenshot-{order_number}.png"
    screenshot_robot(order_number, screenshot_file)
    embed_screenshot_to_receipt(screenshot_file, pdf_file)


def embed_screenshot_to_receipt(screenshot_file, pdf_file):
    """
    Embed the screenshot into the receipt PDF file.

    Args:
        screenshot_file (str): Path to the screenshot file.
        pdf_file (str): Path to the PDF file.
    """
    pdf = PDF()
    pdf.add_files_to_pdf([pdf_file, screenshot_file], target_document=pdf_file)


def screenshot_robot(order_number, screenshot_file):
    """
    Take a screenshot of the robot order.

    Args:
        order_number (str): The order number for the screenshot.
        screenshot_file (str): Path to the screenshot file.
    """
    page = browser.page()
    page.screenshot(path=screenshot_file)


def open_robot_order_website(url):
    """
    Open the robot order website.
    """
    # url = "https://robotsparebinindustries.com/#/robot-order"
    browser.goto(url)


def close_annoying_modal():
    """
    Close the annoying modal that appears on the website.
    """
    page = browser.page()
    page.click("button:text('OK')")


def download_file(url, local_filename):
    """
    Download a file from the given URL and save it locally.

    Args:
        url (str): The URL to download the file from.
        local_filename (str): The local path to save the downloaded file.

    Returns:
        local_filename (str): The local path to the downloaded file.
    """
    response = requests.get(url)
    response.raise_for_status()  # this will raise an exception if the request fails
    with open(local_filename, 'wb') as stream:
        stream.write(response.content)  # write the content of the response to a file
    return local_filename


def archive_receipts():
    """
    Archive the receipts into a zip file.
    """
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'output/receipts.zip', recursive=True)
