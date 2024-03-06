import subprocess
import os
import resource

class CodeJudgeService:
    @staticmethod
    def set_memory_limit(memory_limit_bytes):
        """Set maximum memory usage for child processes."""
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))

    @staticmethod
    def compile_code(source_path):
        """Compiles the C++ code. Returns the path to the executable if successful, None otherwise."""
        executable_path = source_path + '.out'
        compile_process = subprocess.run(['g++', '-o', executable_path, source_path], capture_output=True, text=True)

        if compile_process.returncode != 0:
            print("Compilation Error:", compile_process.stderr)
            return None
        return executable_path
    
    @staticmethod
    def run_test(executable_path, input_text, expected_output, time_limit=2, memory_limit_mb=64):
        """Runs a single test case. Returns True if output matches expected output, False otherwise."""
        # Convert MB to bytes for the memory limit
        memory_limit_bytes = memory_limit_mb * 1024 * 1024
        
        def limit_resources():
            """Function to limit resources, to be called with preexec_fn in subprocess."""
            CodeJudgeService.set_memory_limit(memory_limit_bytes)

        try:
            run_process = subprocess.run(executable_path, input=input_text, capture_output=True, text=True, timeout=time_limit, preexec_fn=limit_resources)
            return True, run_process.stdout.strip() == expected_output.strip()
        except subprocess.TimeoutExpired:
            return False, "Time Limit Exceeded"
        except subprocess.CalledProcessError as e:
            return False, "Runtime Error"

    def judge(self, source_file_path, test_cases_dir, time_limit=2, memory_limit_mb=64):
        """Main judging function. Compiles code and runs it against test cases."""
        executable_path = self.compile_code(source_file_path)
        if not executable_path:
            return False, "Compilation Error"

        
        input_dir = os.path.join(test_cases_dir, 'in')
        output_dir = os.path.join(test_cases_dir, 'out')
        wrong = 0.0
        correct = 0.0
        for test_case in os.listdir(input_dir):
            input_test_case_name = test_case
            output_test_case_name = input_test_case_name.replace('input', 'output')
            with open(os.path.join(input_dir, input_test_case_name), 'r') as input_file, \
                    open(os.path.join(output_dir, output_test_case_name), 'r') as output_file:
                input_text = input_file.read()
                expected_output = output_file.read()
                run_res = self.run_test(executable_path, input_text, expected_output, time_limit, memory_limit_mb)
                if not run_res[0]:
                    raise run_res[1]
                else:
                    if run_res[1]:
                        correct += 1
                    else:
                        wrong += 1
        return True, correct / (correct + wrong)


def main():
    judge_service = CodeJudgeService()
    source_file_path = 'code.cpp'
    test_cases_dir = 'test_cases'
    result = judge_service.judge(source_file_path, test_cases_dir)
    rounded_result = round(result)
    print("Judging Result:", rounded_result)

if __name__ == "__main__":
    main()

