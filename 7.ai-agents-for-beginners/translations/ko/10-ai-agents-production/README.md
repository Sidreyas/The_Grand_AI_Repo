<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "1ad5de6a6388d02c145a92dd04358bab",
  "translation_date": "2025-05-20T08:41:58+00:00",
  "source_file": "10-ai-agents-production/README.md",
  "language_code": "ko"
}
-->
[![AI Agents In Production](../../../translated_images/lesson-10-thumbnail.0b68f4240618b3d5b26693b78cf2cf0a8b36131b50bb08daf91d548cecc87424.ko.png)](https://youtu.be/l4TP6IyJxmQ?si=IvCW3cbw0NJ2mUMV)

> _(위 이미지를 클릭하면 이 강의의 영상을 볼 수 있습니다)_
# AI Agents in Production

## 소개

이번 강의에서는 다음 내용을 다룹니다:

- AI Agent를 효과적으로 프로덕션에 배포하는 방법.
- AI Agent를 프로덕션에 배포할 때 자주 발생하는 실수와 문제점.
- AI Agent의 성능을 유지하면서 비용을 관리하는 방법.

## 학습 목표

이 강의를 마치면 다음을 알게 되거나 이해할 수 있습니다:

- 프로덕션 AI Agent 시스템의 성능, 비용, 효율성을 개선하는 기법.
- AI Agent를 평가하는 방법과 평가할 항목.
- AI Agent를 프로덕션에 배포할 때 비용을 통제하는 방법.

신뢰할 수 있는 AI Agent를 배포하는 것이 중요합니다. "Building Trustworthy AI Agents" 강의도 참고하세요.

## AI Agent 평가하기

AI Agent를 배포하기 전, 배포 중, 그리고 배포 후에 적절한 평가 시스템을 갖추는 것이 매우 중요합니다. 이는 시스템이 사용자와 여러분의 목표에 부합하는지 확인하는 데 도움이 됩니다.

AI Agent를 평가할 때는 단순히 에이전트의 출력만 보는 것이 아니라, AI Agent가 작동하는 전체 시스템을 평가할 수 있어야 합니다. 여기에는 다음과 같은 항목들이 포함되지만 이에 국한되지는 않습니다:

- 초기 모델 요청.
- 사용자의 의도를 파악하는 에이전트의 능력.
- 작업 수행에 적합한 도구를 선택하는 에이전트의 능력.
- 도구가 에이전트의 요청에 응답하는 방식.
- 도구의 응답을 해석하는 에이전트의 능력.
- 에이전트의 응답에 대한 사용자의 피드백.

이렇게 하면 개선할 부분을 모듈별로 구분해서 파악할 수 있습니다. 모델, 프롬프트, 도구 및 기타 구성 요소 변경의 영향을 더 효율적으로 모니터링할 수 있습니다.

## AI Agent에서 자주 발생하는 문제와 해결책

| **문제**                                   | **가능한 해결책**                                                                                                                                                                                                          |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AI Agent가 작업을 일관되게 수행하지 못함   | - AI Agent에게 주는 프롬프트를 명확하게 다듬어 목표를 분명히 하세요.<br>- 작업을 세분화하여 여러 에이전트가 분담할 수 있는지 확인하세요.                                                                              |
| AI Agent가 무한 루프에 빠짐                | - 에이전트가 언제 프로세스를 종료해야 하는지 명확한 종료 조건을 설정하세요.<br>- 복잡한 추론과 계획이 필요한 작업에는 추론에 특화된 더 큰 모델을 사용하세요.                                                          |
| AI Agent의 도구 호출이 제대로 작동하지 않음 | - 에이전트 시스템 외부에서 도구의 출력을 테스트하고 검증하세요.<br>- 도구의 파라미터, 프롬프트, 명칭을 개선하세요.                                                                                                    |
| 다중 에이전트 시스템이 일관되게 작동하지 않음 | - 각 에이전트에게 주는 프롬프트를 구체적이고 명확하게 다듬어 서로 중복되지 않도록 하세요.<br>- "라우팅" 또는 컨트롤러 역할의 에이전트를 만들어 어떤 에이전트가 적합한지 결정하는 계층적 시스템을 구축하세요.           |

## 비용 관리

AI Agent를 프로덕션에 배포할 때 비용을 관리하는 몇 가지 전략은 다음과 같습니다:

- **응답 캐싱** - 자주 발생하는 요청과 작업을 미리 파악하여 에이전트 시스템을 거치기 전에 응답을 제공하면 유사한 요청의 처리량을 줄일 수 있습니다. 기본적인 AI 모델을 활용해 요청이 캐시된 요청과 얼마나 유사한지 판단하는 흐름도 구현할 수 있습니다.

- **소형 모델 사용** - Small Language Models(SLM)는 특정 에이전트용 사용 사례에서 좋은 성능을 내면서 비용을 크게 절감할 수 있습니다. 앞서 언급한 평가 시스템을 구축해 SLM과 대형 모델 간 성능을 비교하는 것이 SLM의 적합성을 판단하는 최선의 방법입니다.

- **라우터 모델 사용** - 다양한 크기와 종류의 모델을 사용하는 전략도 있습니다. 복잡도에 따라 요청을 적합한 모델로 라우팅하는 LLM/SLM 또는 서버리스 함수를 활용할 수 있습니다. 이는 비용 절감뿐 아니라 적절한 작업에서 성능을 보장하는 데도 도움이 됩니다.

## 축하합니다

지금까지 "AI Agents for Beginners"의 마지막 강의를 마쳤습니다.

이 빠르게 성장하는 분야의 피드백과 변화에 맞춰 앞으로도 강의를 추가할 계획이니 가까운 시일 내에 다시 방문해 주세요.

AI Agents와 함께 학습과 개발을 계속하고 싶다면 <a href="https://discord.gg/kzRShWzttr" target="_blank">Azure AI Community Discord</a>에 참여하세요.

워크숍, 커뮤니티 원탁회의, "무엇이든 물어보세요" 세션 등을 진행하고 있습니다.

또한 프로덕션에서 AI Agents를 시작하는 데 도움이 되는 추가 자료를 모은 Learn 컬렉션도 준비되어 있습니다.

## 이전 강의

[Metacognition Design Pattern](../09-metacognition/README.md)

**면책 조항**:  
이 문서는 AI 번역 서비스 [Co-op Translator](https://github.com/Azure/co-op-translator)를 사용하여 번역되었습니다. 정확성을 위해 최선을 다하고 있으나, 자동 번역에는 오류나 부정확한 내용이 포함될 수 있음을 유의하시기 바랍니다. 원문은 해당 언어로 된 원본 문서를 권위 있는 출처로 간주해야 합니다. 중요한 정보의 경우 전문적인 인간 번역을 권장합니다. 본 번역 사용으로 인해 발생하는 오해나 잘못된 해석에 대해 당사는 책임을 지지 않습니다.