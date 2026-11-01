pynk_p Simple FFD 1.0.0
Created by pynk_p | Blender 4.5 이상 | GPL-3.0-or-later

3ds Max FFD에서 착안한 Blender Lattice 작업 도구입니다.
메시 크기에 맞는 격자와 모디파이어를 자동으로 연결합니다.

설치
Preferences > Get Extensions > Install from Disk에서
simple_ffd-1.0.0.zip을 선택합니다. ZIP은 압축 해제하지 않습니다.

사용 방법
1. Object Mode에서 메시 하나를 선택합니다.
2. N 사이드바 > pynk_p > Simple FFD를 엽니다.
3. X/Y/Z 제어점 수(각 2~16개)를 입력하고 Create Grid를 누릅니다.
4. 제어점을 선택하고 G/S/R로 변형합니다.
5. Finish Editing으로 마치고, Edit Control Points로 다시 편집합니다.

참고
- 숫자는 칸 수가 아닌 제어점 수입니다.
- Update Grid는 새 개수를 적용하고 기존 변형을 초기화합니다.
  같은 개수로 눌러도 초기화되며, 숫자 입력만으로는 변형되지 않습니다.
- Reset Deformation은 개수를 유지하며 변형만 초기화합니다.
- Finish Editing은 모디파이어 Apply가 아닙니다.
- Blender Lattice의 B-Spline 보간을 사용해 Max FFD와 결과가 다를 수 있습니다.

Blender 4.5.5 / 5.2.3에서 백그라운드 테스트 완료.
검증 범위와 제한은 VALIDATION.txt를 참고하세요.
