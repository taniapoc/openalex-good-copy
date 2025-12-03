# This code runs all of the files to clean the data and run the dashboard, without pulling the new data
# The purpose of this is mostly for testing, including making sure that changes to one file do not break the whole sequence, or overwrite certain files. 

def main():
    import os 
    import papermill as pm
    from datetime import datetime
    import subprocess
    import sys
    import socket
    import psutil
    import time
    #from rioSendEmail import sendEmail

    # check port 8050 and kill existing process if needed 
    PORT = 8050

    # First check if the port is in use
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", PORT))
            print(f"Port {PORT} is free.")
        except OSError:
            # Port is in use -> find and kill the process
            killed_any = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.net_connections(kind='inet'):
                        if conn.laddr.port == PORT:
                            print(f"Killing process {proc.pid} ({proc.name()}) using port {PORT}")
                            proc.kill()
                            killed_any = True
                            time.sleep(1)  # wait a bit for OS to free port
                            break
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
            if not killed_any:
                print(f"Port {PORT} is in use, but no process could be killed.")

    # set up file path and different tasks to run
    os.chdir('/Users/administrator/Desktop/openalex dashboards')

    tasks = ["data_pull_scripts/2. institution overview info.ipynb", 
            "data_pull_scripts/3. topics and subject areas.ipynb",
            "data_pull_scripts/4. topics detailed tables.ipynb",
            "data_pull_scripts/5. detailed works cleaning.ipynb",
            "data_pull_scripts/6. topics page.ipynb",
            "data_pull_scripts/7. SDGs page.ipynb",
            "data_pull_scripts/8. authors data cleaning.ipynb"#,
            #"render_openalex_dashboard.ipynb"
            ]

    log_root_path = "/Users/administrator/Desktop/openalex dashboards/notes/"

    # run the preliminary tasks 
    for task in tasks:
        try:
            out_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "_" + os.path.basename(task)
            out_path = os.path.join(log_root_path, out_name)

            pm.execute_notebook(
                task,
                out_path, 
                cwd=os.path.dirname(task)
            )

            print(f'{task} is done running')
        
        except Exception as e: 
            #sendEmail(
            print('oopsie daisy')
            #)



    print("preprocessing is done, running dash app next ")

    # convert notebook containing dash app to a .py script 
    # this allows me to develop/test in the notebook, but it needs to be in a .py for the subprocess to work, so this is the solution
    dash_notebook = "render_openalex_dashboard.ipynb"
    dash_script = "render_openalex_dashboard.py"
    subprocess.run([
        sys.executable, "-m", "jupyter", "nbconvert",
        "--to", "script", dash_notebook
    ], check=True)

    print(f'notebook succesfully converted')

    # Start the Dash app
    print(f'launcing dash app now')
    subprocess.Popen([sys.executable, dash_script])

    print("if the dashboard doesn't open automatically, it is available at:")
    print("http://127.0.0.1:8050")

    print(" IMPORTANT: please make sure to close out the Dash process (Ctrl + C) when you are done viewing the dashboard!! Just close the browser tab and not doing this step may cause problems the next time you wish to open the dashboards. Thanks!")


if __name__ == '__main__': main()