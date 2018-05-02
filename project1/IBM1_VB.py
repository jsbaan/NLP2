from collections import defaultdict
import math
from perplexity import perplexity
import pickle
from scipy.special import digamma

## Expectation Maximization (EM)
def IBM1_VB(e,f,lexicon,nr_it=10):
    print('--Performing EM--')

    for it in range(nr_it):
        # Keep track of counts to be used for the M step
        norm_count_e_f = defaultdict(lambda: defaultdict(float))
        norm_count_e = defaultdict(float)
        count_e_f = defaultdict(lambda: defaultdict(int))
        count_e = defaultdict(int)

        # Keep track of lambda: matrix that governs the dirichlet prior parameters
        dir_prior = lexicon.copy()


        # Expectation
        print('Expectation...')
        perplex = 0
        for (e_sent,f_sent) in zip(e,f):
            # Initialize likelihoods
            alignment_likelihood = 1

            # TODO use Q??
            sentence_likelihood = 1/(len(e_sent)**len(f_sent))
            for j, f_word in enumerate(f_sent):
                # Sum of all alignment link probabilities from current f word to all words in e
                sum_pi_t = sum([dir_prior[e_word][f_word] for e_word in e_sent])
                sentence_likelihood *= sum_pi_t

                for a_j, e_word in enumerate(e_sent):
                    # Single alignment link probability
                    pi_t = dir_prior[e_word][f_word]

                    # Ratio between single link and summed link alignment probabilities
                    ratio = math.exp(digamma(pi_t)-digamma(sum_pi_t))
                    alignment_likelihood *= ratio

                    # Update counts
                    # count_e_f[e_sent[a_j]][f_sent[j]] += pi_t
                    # count_e[e_sent[a_j]] += pi_t

                    # Update normalized counts
                    norm_count_e_f[e_sent[a_j]][f_sent[j]] += ratio
                    norm_count_e[e_sent[a_j]] += ratio

            # TODO should we skip big/unlikely sentences in this way?
            if sentence_likelihood > 0:
                perplex -=math.log(sentence_likelihood,2)
        print('[Iteration {}] perplexity: {}'.format(it+1, round(perplex)))

        # Maximization
        print('Maximization')
        for e_word, f_words in dir_prior.items():
            for f_word, prob in f_words.items():
                dir_prior[e_word][f_word] = norm_count_e_f[e_word][f_word] / float(norm_count_e[e_word])

    return dir_prior