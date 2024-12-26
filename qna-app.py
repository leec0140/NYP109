from dotenv import load_dotenv
import os
import requests

# Import namespaces
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

def main():
    try:
        # Get Configuration Settings
        load_dotenv()
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')
        ai_project_name = os.getenv('QA_PROJECT_NAME')
        ai_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')
        # Translator API details
        translator_endpoint = os.getenv('translator_endpoint')
        translator_key = os.getenv('translator_key')
        headers = {
            "Ocp-Apim-Subscription-Key": translator_key,
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Region": "eastus"  # e.g., "eastus"
        }

        # Create client using endpoint and key
        credential = AzureKeyCredential(ai_key)
        ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=credential)

        # Submit a question and display the answer
        user_question = ''
        while user_question.lower() != 'quit':
            user_question = input('\nQuestion:\n')

            # Detect language
            params = {'api-version': '3.0'}
            body = [{'text': user_question}]
            response = requests.post(f"{translator_endpoint}/detect", headers=headers, json=body, params=params)
            detected_language = response.json()[0]['language']
            print(f"Detected Language: {detected_language}")
            
            # Translate text to English
            translate_params = {
                'api-version': '3.0',
                'to': ['en']  # Target language
            }
            translate_response = requests.post(f"{translator_endpoint}/translate", headers=headers, json=body, params=translate_params)
            translated_text = translate_response.json()[0]['translations'][0]['text']
            print(f"Translated Text: {translated_text}")

            response = ai_client.get_answers(question=translated_text,
                                            project_name=ai_project_name,
                                            deployment_name=ai_deployment_name)
            for candidate in response.answers:
                print(f"Bot's Answer: {candidate.answer}")
                print("Confidence: {}".format(candidate.confidence))
                print("Source: {}".format(candidate.source))
            
            # Translate response back to user's language
            answers = response.answers  # Assuming 'answers' is an attribute of 'AnswersResult'
            response_text = answers[0].answer  # Access the 'answer' attribute
            response_body = [{'text': response_text}]
            response_translate_params = {
                'api-version': '3.0',
                'to': [detected_language]  # Translate back to user's language
            }
            response_translation = requests.post(f"{translator_endpoint}/translate", headers=headers, json=response_body, params=response_translate_params)
            final_response = response_translation.json()[0]['translations'][0]['text']
            print(f"Translated Bot Response: {final_response}")
            

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
