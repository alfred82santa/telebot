import os

from aiotelebot.telegram_api_spec import spec

MOCK_DIR = os.path.join(os.path.dirname(__file__), 'data', 'mocks')

spec['get_me']['mock'] = {'mock_type': 'RawFileMock',
                          'file': os.path.join(MOCK_DIR, 'get_me.json')}

spec['get_updates']['mock'] = {'mock_type': 'RawFileMock',
                               'file': os.path.join(MOCK_DIR, 'get_updates_empty.json')}

spec['get_file']['mock'] = {'mock_type': 'RawFileMock',
                            'file': os.path.join(MOCK_DIR, 'get_file.json')}

spec['download_file']['mock'] = {'mock_type': 'RawFileMock',
                                 'file': os.path.join(MOCK_DIR, 'download_file.json')}

spec['get_user_profile_photos']['mock'] = {'mock_type': 'RawFileMock',
                                           'file': os.path.join(MOCK_DIR, 'get_user_profile_photos.json')}

spec['set_webhook']['mock'] = {'mock_type': 'RawFileMock',
                               'file': os.path.join(MOCK_DIR, 'set_webhook.json')}

spec['send_message']['mock'] = {'mock_type': 'RawFileMock',
                                'file': os.path.join(MOCK_DIR, 'send_message.json')}

spec['send_location']['mock'] = {'mock_type': 'RawFileMock',
                                 'file': os.path.join(MOCK_DIR, 'send_location.json')}

spec['forward_message']['mock'] = {'mock_type': 'RawFileMock',
                                   'file': os.path.join(MOCK_DIR, 'forward_message.json')}

spec['send_photo']['mock'] = {'mock_type': 'RawFileMock',
                              'file': os.path.join(MOCK_DIR, 'send_photo.json')}

spec['send_audio']['mock'] = {'mock_type': 'RawFileMock',
                              'file': os.path.join(MOCK_DIR, 'send_audio.json')}

spec['send_document']['mock'] = {'mock_type': 'RawFileMock',
                                 'file': os.path.join(MOCK_DIR, 'send_document.json')}

spec['send_sticker']['mock'] = {'mock_type': 'RawFileMock',
                                'file': os.path.join(MOCK_DIR, 'send_sticker.json')}

spec['send_video']['mock'] = {'mock_type': 'RawFileMock',
                              'file': os.path.join(MOCK_DIR, 'send_video.json')}

spec['send_voice']['mock'] = {'mock_type': 'RawFileMock',
                              'file': os.path.join(MOCK_DIR, 'send_voice.json')}

spec['send_venue']['mock'] = {'mock_type': 'RawFileMock',
                              'file': os.path.join(MOCK_DIR, 'send_venue.json')}

spec['send_contact']['mock'] = {'mock_type': 'RawFileMock',
                                'file': os.path.join(MOCK_DIR, 'send_contact.json')}

spec['send_chat_action']['mock'] = {'mock_type': 'RawFileMock',
                                    'file': os.path.join(MOCK_DIR, 'send_chat_action.json')}

spec['answer_inline_query']['mock'] = {'mock_type': 'RawFileMock',
                                       'file': os.path.join(MOCK_DIR, 'answer_inline_query.json')}

spec['answer_callback_query']['mock'] = {'mock_type': 'RawFileMock',
                                         'file': os.path.join(MOCK_DIR, 'answer_callback_query.json')}

spec['edit_message_text']['mock'] = {'mock_type': 'RawFileMock',
                                     'file': os.path.join(MOCK_DIR, 'edit_message_text.json')}

spec['edit_message_caption']['mock'] = {'mock_type': 'RawFileMock',
                                        'file': os.path.join(MOCK_DIR, 'edit_message_caption.json')}

spec['edit_message_reply_markup']['mock'] = {'mock_type': 'RawFileMock',
                                             'file': os.path.join(MOCK_DIR, 'edit_message_reply_markup.json')}

spec['kick_chat_member']['mock'] = {'mock_type': 'RawFileMock',
                                    'file': os.path.join(MOCK_DIR, 'kick_chat_member.json')}

spec['leave_chat']['mock'] = {'mock_type': 'RawFileMock',
                              'file': os.path.join(MOCK_DIR, 'leave_chat.json')}

spec['unban_chat_member']['mock'] = {'mock_type': 'RawFileMock',
                                     'file': os.path.join(MOCK_DIR, 'unban_chat_member.json')}

spec['get_chat']['mock'] = {'mock_type': 'RawFileMock',
                            'file': os.path.join(MOCK_DIR, 'get_chat.json')}

spec['get_chat_administrators']['mock'] = {'mock_type': 'RawFileMock',
                                           'file': os.path.join(MOCK_DIR, 'get_chat_administrators.json')}

spec['get_chat_members_count']['mock'] = {'mock_type': 'RawFileMock',
                                          'file': os.path.join(MOCK_DIR, 'get_chat_members_count.json')}

spec['get_chat_member']['mock'] = {'mock_type': 'RawFileMock',
                                   'file': os.path.join(MOCK_DIR, 'get_chat_member.json')}

mock_spec = spec
