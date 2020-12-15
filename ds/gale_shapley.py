from typing import Callable, Generic, TypeVar, List, Optional, Tuple

A = TypeVar("A")
B = TypeVar("B")


class GaleShapley(Generic[A, B]):
    def __init__(
        self,
        # returns the preference level. (None if this A would never invite this B)
        pref_a_b: Callable[[A, B], Optional[int]],
        pref_b_a: Callable[[B, A], int],
    ):
        self._pref_a_b = pref_a_b
        self._pref_b_a = pref_b_a

    def match(self, lst_a: List[A], lst_b: List[B]) -> List[Tuple[int, int]]:
        n_as = len(lst_a)
        n_bs = len(lst_b)

        a_invitelists = {
            a: sorted(
                [
                    b
                    for b in range(n_bs)
                    if self._pref_a_b(lst_a[a], lst_b[b]) is not None
                ],
                key=lambda b: self._pref_a_b(lst_a[a], lst_b[b]),
            )
            for a in range(n_as)
        }

        matched_a_s = set()
        mailboxes_b = {b: None for b in range(n_bs)}

        def invite(new_a, b):
            old_a = mailboxes_b[b]
            use_a, discard_a = (
                (new_a, old_a)
                if old_a is None
                else (new_a, old_a)
                if self._pref_b_a(lst_b[b], lst_a[new_a])
                > self._pref_b_a(lst_b[b], lst_a[old_a])
                else (old_a, new_a)
            )
            mailboxes_b[b] = use_a
            return discard_a

        while True:
            # clear empty lists
            a_invitelists = {k: v for k, v in a_invitelists.items() if len(v) != 0}

            if len(a_invitelists) == 0:
                break

            # try for matchings
            for a in list(a_invitelists):
                if a in matched_a_s:
                    continue  # don't look at it

                b = a_invitelists[a].pop()

                matched_a_s.add(a)
                matched_a_s.discard(invite(a, b))

            matchable_as = set(matched_a_s) - set(a_invitelists.keys())
            if len(matchable_as) == 0:
                break

        return [(a, b) for b, a in mailboxes_b.items() if a is not None]
