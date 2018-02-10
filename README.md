# AppWorx to Jenkins Converter

Python Script which converts AppWorx job (module) or processes flow (chain) to Jenkins job.

## Usage

1. Export the job description (.exp file) from AppWorx
2. Install required packages:

    ```
    $ pip install -r requirements.txt
    ```

3. Run the script:

    ```
    $ python appworx_jenkins_converter.py \
          /path/to/.exp/file \
          jenkins_url \
          jenkins_username \
          jenkins_token
    ```

    You can also export the `config.xml` by:

    ```
    $ python appworx_jenkins_converter.py \
          /path/to/.exp/file \
          jenkins_url \
          jenkins_username \
          jenkins_token > config.xml
    ```
