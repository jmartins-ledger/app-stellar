#include <string.h>
#include <stdint.h>

#include "swap_lib_calls.h"
#include "stellar_api.h"

/* return 0 on error, 1 otherwise */
int handle_get_printable_amount(get_printable_amount_parameters_t* params) {
    uint64_t amount;

    params->printable_amount[0] = '\x00';

    if (!swap_str_to_u64(params->amount, params->amount_length, &amount)) {
        PRINTF("Amount is too big");
        return 0;
    }

    BEGIN_TRY {
        TRY {
            print_amount(amount, "XLM", params->printable_amount);
        }
        CATCH_ALL {
            return 0;
        }
        FINALLY {
        }
    }
    END_TRY;

    return 1;
}