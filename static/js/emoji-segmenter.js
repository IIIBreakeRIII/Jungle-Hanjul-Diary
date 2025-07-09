export function setupGraphemeLimiter({
	inputSelector,
	maxChars,
	locale = 'ko'
}) {
	// segmenter 선언
	const segmenter = new Intl.Segmenter(locale, { granularity: 'grapheme' });
	// inputSelector로부터 쿼리 내 내용을 받아옴
	const inputs = document.querySelectorAll(inputSelector);

	// eventListener 등록 후 input의 변화에 따라 로직 수행
	inputs.forEach(input => {
		input.addEventListener('input', () => {
			// 입력값을 grapheme 단위로 쪼개 배열로 생성 => 형태는 { segment: "문자" }
			const segments = Array.from(segmenter.segment(input.value));
			// 실제 문자만 뽑아 배열로 만듦 => segment 단위로 쪼갠다는 뜻 (아래에서 자세하게 설명)
			const chars = segments.map(seg => seg.segment);
			// 만약, maxChars 보다 현재 받아온 세그먼트 전체의 개수가 많아진다면,
			if (chars.length > maxChars) {
				// 0번째부터 마지막 50번째 객체 까지만 slice, 나머지는 버림
				input.value = chars.slice(0, maxChars).join('');
			}
		})
	})
}

// consts chars = segments.map(seg => seg.segment) 에 대한 자세한 설명
// 아래와 같이 segments의 반환 값은 {세그먼트 / 인덱스 / 워드의 형태인지} 로 반환
// 여기에서 워드가 아닐 경우는, 세그먼트의 개수에 따라가도록 설계한 것

// const segmenter = new Intl.Segmenter('ko', { granularity: 'grapheme' });
// const segments = Array.from(segmenter.segment('안녕😊하세요'));

// output
// segments = [
//   {segment: '안', index: 0, isWordLike: true},
//   {segment: '녕', index: 1, isWordLike: true},
//   {segment: '😊', index: 2, isWordLike: false},
//   {segment: '하', index: 3, isWordLike: true},
//   {segment: '세', index: 4, isWordLike: true},
//   {segment: '요', index: 5, isWordLike: true}
// ]