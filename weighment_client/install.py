
import click

from weighment_client.setup import before_install as setup


def before_install():
	try:
		print("Setting up Weighment Client...")
		setup()

		click.secho("Thank you for installing Weighment Client!", fg="green")

	except Exception as e:
		BUG_REPORT_URL = "https://github.com/asoral/weighment_client/issues/new"
		click.secho(
			"Installation for Weighment Client app failed due to an error."
			" Please try re-installing the app or"
			f" report the issue on {BUG_REPORT_URL} if not resolved.",
			fg="bright_red",
		)
		raise e