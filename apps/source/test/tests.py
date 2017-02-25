from apps.source.models import OnlySourceCode
from django.http import HttpResponse
import shortuuid


def test_run(self):
    __code = '#include <cstdio> \
        #define mx 1000005 \
        int n, data[mx], Left[mx << 2], Right[mx << 2], temp, edL, edR; \
        long long add[mx]; \
        void push(int *ts, int L, int R, int now){ \
            if (L <= temp && temp <= R){ \
                ++ts[now]; \
                if (L == R) return; \
            } \
            int mid = L + R >> 1; \
            if (temp > mid) push(ts, ++mid, R, now << 1 | 1); \
            else push(ts, L, mid, now << 1); \
        } \
        void pop(int *ts, int L, int R, int now){ \
            if (L <= temp && temp <= R){ \
                --ts[now]; \
                if (L == R) return; \
            } \
            int mid = L + R >> 1; \
            if (temp > mid) pop(ts, ++mid, R, now << 1 | 1); \
            else pop(ts, L, mid, now << 1); \
        } \
        int sum(int *ts, int L, int R, int now){ \
            if (edL <= L  &&   R <= edR) return ts[now]; \
            if (edR < L || R < edL) return 0; \
            int mid = L + R >> 1; \
            return sum(ts, L, mid, now << 1) + sum(ts, mid + 1, R, now << 1 | 1); \
        } \
        int main(){ \
            int i, stL = 0, stR = 1000000; \
            for (i = 1; i < mx; ++i) add[i] = add[i - 1] + i; \
            scanf("%d", &n); \
            for (i = 0; i < n; ++i){ \
                scanf("%d", &data[i]); \
                temp = data[i]; \
                push(Right, stL, stR, 1); \
            } \
            long long opt = 0; \
            for (i = 0; i < n; ++i){ \
                temp = 0; \
                edL = data[i] + 1; edR = stR; \
                temp += sum(Left, stL, stR, 1); \
                edL = 0; edR = data[i] - 1; \
                temp += sum(Right, stL, stR, 1); \
                opt += add[temp]; \
                temp = data[i]; \
                pop(Right, stL, stR, 1); push(Left, stL, stR, 1); \
            } \
            printf("%lld", opt); \
            return 0; \
        }'
    for i in xrange(0, 1000000):
        print i
        only_source_code = OnlySourceCode(
            uuid=shortuuid.uuid(),
            poster='test',
            source=__code.encode('utf-8'),
            lexer='cpp',
        )
        only_source_code.save()

    return HttpResponse("ok")
