import re
from collections import defaultdict, Counter


# Load word list from file and filter words based on specified word length
def load_word_list(file_path, word_length):
	with open(file_path, 'r', encoding='utf-8') as file:
		# Only keep words that match the specified length
		words = [word.strip().lower() for word in file if len(word.strip()) == word_length]
	return words


# Filter words using a regex pattern that matches the correct and misplaced letters
def filter_words_by_regex(words, correct_positions, misplaced_letters, absent_letters):
	# Build regex pattern for filtering words
	pattern = ''
	for idx, letter in enumerate(correct_positions):
		if letter:  # If the position has a known correct letter
			pattern += letter
		else:  # For unknown letters
			# Create a set of letters that should not be in this position (misplaced or absent letters)
			not_here = ''.join(
				misplaced_letters.get(letter, []) for letter in misplaced_letters if idx in misplaced_letters[letter])
			# Exclude absent letters and misplaced letters from this position
			excluded = ''.join(absent_letters) + not_here
			pattern += f"[^{excluded}]" if excluded else '.'  # '.' matches any letter

	# Compile the regex pattern
	regex = re.compile(pattern)

	# Filter words that match the regex pattern
	filtered_words = [word for word in words if regex.match(word)]

	# Further filter out words where misplaced letters are in the wrong positions
	for letter, positions in misplaced_letters.items():
		filtered_words = [word for word in filtered_words if all(word[idx] != letter for idx in positions)]

	return filtered_words


# Calculate the frequency of letters at each position and total letter frequency
def calculate_letter_frequencies(words):
	letter_frequencies = [Counter() for _ in range(len(words[0]))]  # Frequency of each letter at each position
	total_letter_frequencies = Counter()  # Frequency of each letter across all positions

	for word in words:
		for idx, letter in enumerate(word):
			letter_frequencies[idx][letter] += 1  # Count letter frequency at each position
		total_letter_frequencies.update(word)  # Count total frequency of each letter

	return letter_frequencies, total_letter_frequencies


# Score a word based on letter frequency at each position and overall frequency
def score_word(word, letter_frequencies, total_letter_frequencies):
	score = 0
	unique_letters = set(word)  # Use unique letters to avoid over-counting repeated letters

	# Add score based on the frequency of the letter in each position
	for idx, letter in enumerate(word):
		score += letter_frequencies[idx][letter]

	# Add score based on the overall frequency of the letter in the word
	for letter in unique_letters:
		score += total_letter_frequencies[letter]

	return score


# Filter words that contain unique letters (no repeated letters)
def filter_unique_letter_words(words):
	return [word for word in words if len(set(word)) == len(word)]  # Filter words with non-repeating letters


# Suggest the best word based on letter frequency, prioritizing words with unique letters
def suggest_word(words):
	if not words:
		return None

	# Prioritize words with unique letters
	unique_letter_words = filter_unique_letter_words(words)

	# If there are words with unique letters, score and suggest the best one
	if unique_letter_words:
		letter_frequencies, total_letter_frequencies = calculate_letter_frequencies(unique_letter_words)
		best_word = max(unique_letter_words,
		                key=lambda word: score_word(word, letter_frequencies, total_letter_frequencies))
	else:
		# If no words have unique letters, use the full list of words
		letter_frequencies, total_letter_frequencies = calculate_letter_frequencies(words)
		best_word = max(words, key=lambda word: score_word(word, letter_frequencies, total_letter_frequencies))

	return best_word


# Main function: Interactive input from user to filter and suggest words
def wordle_solver(word_list_file):
	word_length = int(input("Enter the word length: "))  # User input for word length
	words = load_word_list(word_list_file, word_length)  # Load word list from file

	correct_positions = [None] * word_length  # List to store correct letters in known positions
	misplaced_letters = defaultdict(list)  # Dictionary to store misplaced letters (present but in the wrong position)
	absent_letters = set()  # Set to store letters that are known to be absent

	while True:
		print("\nPlease enter the following information:")
		# Input known correct positions, using '_' or space for unknown positions
		known_positions = input(
			f"Known letter positions (use _ for unknowns, length must be {word_length}, e.g., 'a__le'): ").lower()
		# Input letters that are known but not in the correct position
		unknown_position_letters = input("Known letters but position unknown (no spaces, e.g., 'ae'): ").lower()
		# Input letters that are known to be absent
		absent_letters_input = input("Letters known to be absent (no spaces, e.g., 'xyz'): ").lower()

		# Process input for known positions
		if known_positions:
			correct_positions = [ch if ch != '_' else None for ch in known_positions]

		# Process input for known but misplaced letters
		if unknown_position_letters:
			for letter in unknown_position_letters:
				if letter not in misplaced_letters:
					misplaced_letters[letter] = []

		# Process input for absent letters
		if absent_letters_input:
			absent_letters.update(absent_letters_input)

		# Filter the list of words based on the user input using regular expressions
		words = filter_words_by_regex(words, correct_positions, misplaced_letters, absent_letters)

		if words:  # If there are words that match the criteria
			suggestion = suggest_word(words)  # Suggest the best word based on letter frequency
			print(f"The recommended word is: {suggestion}")
		else:  # If no words match the criteria
			print("No matching words found. Please check your input.")
			break

		# Ask if the user wants to continue filtering
		continue_search = input("Would you like to continue filtering? (y/n): ").lower()
		if continue_search != 'y':
			break


# Example: Start the solver
wordle_solver("wordlist.txt")
