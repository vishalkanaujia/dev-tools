#include <stdio.h>
#include <stddef.h>

#if 0
char *s = "\n  \t   \n  a   \n  \r\n bc  \t  \t d";
4 3 2

char *s = "a";
1 1 1

1. line is identified with \n \r
2. char all except whitespaces
3. words, \t and ' '
#endif

int  printable_char(char *p)
{
	if (*p == ' ' ||
			*p == '\t' ||
			*p == '\n' ||
			*p == '\0' ||
			*p == '\r') {
		return 0;
	}
	return 1;
}

/* Only four whitespace chars are: ' ', '\t', '\n', '\r' */
void print_num_printable_chars_words_lines(char *str) {
	char *pp = str;

	// Case 1. Empty string
	if (pp == NULL || *pp == '\0') {
		printf("char=%d words=%d lines=%d\n", 0,0,0);
		return;
	}

	// case 2. String with n chars    

	// states for words and lines
	// Initial states are set to zero
	int m = 0, n = 0;

	// Count for chars, words and lines
	int c = 0, w = 0, l = 0;
	char *p = str;

	while (p) {
		p = pp;
		pp++;       
		// Count the printable characters

		// Set the m state 
		if (printable_char(p)) {
			m = 1;
			c++;
			continue;   
		} else {
			// We have seen a special character

			// Process for words
			if ((*p == ' ' ||
					*p == '\t') &&
					m == 1) {
				// we have seen 1 or n chars together
				w++;
				n = 1;
				m = 0;
			}

			// Process for lines
			if (*p == '\n' ||
					*p == '\r') {

				if (n == 1) {
					l++;
					n = 0;
					m = 0;
				}

				if (m == 1) {
					l++;
					w++;
					n = m = 0;
				}
			} // end process lines

			if (*p == '\0') {
				if (m == 1) {
					l++; w++;
				} else if (n == 1) {
					l++;
				}
				p = NULL;
			}
		} // end process special chars
	} // end of while

	printf("char=%d words=%d lines=%d\n", c,w,l);
}

int main()
{
	print_num_printable_chars_words_lines("a\nb");
	print_num_printable_chars_words_lines("\n  \t   \n  a   \n  \r\n bc  \t  \t d");
	print_num_printable_chars_words_lines("a");
}
