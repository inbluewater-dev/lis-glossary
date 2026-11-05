# 문헌정보학 용어사전 (Korean Glossary of Library and Information Science)

도서관과 정보에 관한 핵심 용어 100개를 누구나 이해할 수 있는 말로 풀어 쓴 한국어 용어사전입니다.

- 웹: https://inbluewater-dev.github.io/lis-glossary/
- AI용 안내: https://inbluewater-dev.github.io/lis-glossary/llms.txt
- 전체 데이터: [`glossary.json`](https://inbluewater-dev.github.io/lis-glossary/glossary.json) · [`llms-full.txt`](https://inbluewater-dev.github.io/lis-glossary/llms-full.txt)

## 구성

| 경로 | 내용 |
|---|---|
| `data/terms.yaml` | **본문 정본.** 용어·영어·다른 이름·분야·정의·예·관련어·근거 |
| `data/sources.yaml` | 근거 자료 목록 |
| `build.py` | 정본에서 `docs/` 전체를 만드는 생성기 (`python3 build.py`, PyYAML 필요) |
| `docs/` | GitHub Pages로 공개되는 사이트. **손으로 고치지 않습니다** — 빌드할 때마다 새로 만들어집니다 |

## 정의에 대하여

모든 정의는 이 사전을 위해 새로 쓴 문장이며, 기존 사전의 문장을 옮겨 오지 않았습니다.
각 용어의 「근거」는 정의를 쓸 때 기댄 국제 표준·법령·기관 자료입니다.

정의는 AI(Anthropic의 Claude)의 도움을 받아 작성했으며, 별도의 검수 과정에서 사실관계를 근거 자료와 대조했습니다.

## 이용 허락

본문과 데이터는 [크리에이티브 커먼즈 저작자표시 4.0 국제 라이선스(CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.ko)로 공개합니다.
출처를 「문헌정보학 용어사전 (https://inbluewater-dev.github.io/lis-glossary/)」처럼 밝히면 누구나 자유롭게 쓸 수 있습니다.
