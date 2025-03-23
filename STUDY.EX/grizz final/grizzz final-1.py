from tkinter import * 
from tkinter import ttk, scrolledtext, filedialog
from openai import OpenAI
import threading

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Assistant - Gemma-3B")
        
        # Create main container
        self.mainframe = ttk.Frame(root, padding="10")
        self.mainframe.grid(row=0, column=0, sticky=(N, S, E, W))
        
        # Create input sections
        self.create_input_sections()
        self.create_file_upload_section()
        self.create_action_button()
        self.create_response_area()
        
        # Status bar
        self.status = ttk.Label(root, text="All fields required", anchor=W)
        self.status.grid(row=1, column=0, sticky=(W, E))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Set up input validation
        self.setup_validation()

    def create_input_sections(self):
        # Interest Section
        self.interest_frame = ttk.LabelFrame(self.mainframe, text="Current Studies")
        self.interest_frame.grid(row=0, column=0, sticky=(E, W), pady=5)
        self.interest_text = Text(self.interest_frame, height=4, width=50)
        self.interest_text.grid(row=0, column=0, padx=5, pady=5)
        
        # Skill Level Section
        self.skill_frame = ttk.LabelFrame(self.mainframe, text="Skill Level")
        self.skill_frame.grid(row=1, column=0, sticky=(E, W), pady=5)
        self.skill_text = Text(self.skill_frame, height=4, width=50)
        self.skill_text.grid(row=0, column=0, padx=5, pady=5)
        
        # Study Area Section
        self.study_frame = ttk.LabelFrame(self.mainframe, text="Your Interest")
        self.study_frame.grid(row=2, column=0, sticky=(E, W), pady=5)
        self.study_text = Text(self.study_frame, height=4, width=50)
        self.study_text.grid(row=0, column=0, padx=5, pady=5)
        
        # Learning Section
        self.learning_frame = ttk.LabelFrame(self.mainframe, text="What Are You Learning?")
        self.learning_frame.grid(row=3, column=0, sticky=(E, W), pady=5)
        self.learning_text = Text(self.learning_frame, height=4, width=50)
        self.learning_text.grid(row=0, column=0, padx=5, pady=5)

    def create_file_upload_section(self):
        self.file_frame = ttk.LabelFrame(self.mainframe, text="Upload Study Materials")
        self.file_frame.grid(row=4, column=0, sticky=(E, W), pady=5)
        self.upload_button = ttk.Button(self.file_frame, text="Upload File", command=self.upload_file)
        self.upload_button.grid(row=0, column=0, padx=5, pady=5)
        self.file_label = ttk.Label(self.file_frame, text="No file uploaded")
        self.file_label.grid(row=0, column=1, padx=5, pady=5)
    
    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_label.config(text=f"Uploaded: {file_path.split('/')[-1]}")

    def create_action_button(self):
        self.send_btn = ttk.Button(
            self.mainframe,
            text="help",
            command=self.validate_and_send,
            state=DISABLED
        )
        self.send_btn.grid(row=5, column=0, pady=10)

    def create_response_area(self):
        response_frame = ttk.LabelFrame(self.mainframe, text="Study Plan")
        response_frame.grid(row=6, column=0, sticky=(N, S, E, W), pady=5)
        
        self.response_text = scrolledtext.ScrolledText(
            response_frame, 
            height=12,
            wrap=WORD
        )
        self.response_text.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def setup_validation(self):
        for text_widget in [self.interest_text, self.skill_text, self.study_text, self.learning_text]:
            text_widget.bind("<KeyRelease>", self.check_fields)

    def check_fields(self, event=None):
        all_filled = all([
            self.interest_text.get("1.0", END).strip(),
            self.skill_text.get("1.0", END).strip(),
            self.study_text.get("1.0", END).strip(),
            self.learning_text.get("1.0", END).strip()
        ])
        self.send_btn.config(state=NORMAL if all_filled else DISABLED)
        self.status.config(text="Ready" if all_filled else "All fields required")

    def validate_and_send(self):
        interest = self.interest_text.get("1.0", END).strip()
        skill = self.skill_text.get("1.0", END).strip()
        study = self.study_text.get("1.0", END).strip()
        learning = self.learning_text.get("1.0", END).strip()
        
        combined_prompt = f"""treat me like im a student:
        - Interest: {interest}
        - Skill Level: {skill}
        - Current Studies: {study}
        - Learning Topic: {learning}
        
        Provide a help to what the student ask."""
        
        self.update_status("Generating...")
        self.toggle_ui(state=False)
        
        threading.Thread(
            target=self.process_prompt,
            args=(combined_prompt,)
        ).start()

    def process_prompt(self, prompt):
        try:
            response = client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": "You are an expert learning teacher helping a student."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            result = response.choices[0].message.content
            self.display_response(f"help a student:\n{result}\n{'='*50}\n")
            
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
        finally:
            self.toggle_ui(state=True)
            self.update_status("Ready")

    def display_response(self, text):
        self.response_text.config(state=NORMAL)
        self.response_text.delete(1.0, END)
        self.response_text.insert(END, text)
        self.response_text.config(state=DISABLED)

    def update_status(self, message):
        self.status.config(text=message)

    def show_error(self, message):
        self.response_text.config(state=NORMAL)
        self.response_text.insert(END, f"ERROR: {message}\n")
        self.response_text.config(state=DISABLED)
        self.status.config(text=message)

    def toggle_ui(self, state):
        self.send_btn.config(state=NORMAL if state else DISABLED)
        for widget in [self.interest_text, self.skill_text, self.study_text, self.learning_text]:
            widget.config(state=NORMAL if state else DISABLED)

if __name__ == "__main__":
    root = Tk()
    root.geometry("800x750")
    ChatGUI(root)
    root.mainloop()